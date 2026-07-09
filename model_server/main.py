from fastapi import FastAPI
from fastmcp import Client
from pydantic import BaseModel
import os
import base64
import requests
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()


def encode_b64(text: str) -> str:
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


app = FastAPI(title='Model Server')


class AskRequest(BaseModel):
    question: str


def policy_gate(question: str) -> dict:
    """Check whether a prompt is allowed before routing to tools or the model"""
    blocked_terms = {
        "patient name": "Requests patient-identifying informaion", 
        "names": "Requests patient-identifying informaion", 
        "mrn": "Requests medical record numbers", 
        "dob": "Requests patient-identifying informaion", 
        "date of birth": "Requests patient-identifying informaion", 
        "address": "Requests patient-identifying informaion", 
        "phone number": "Requests patient-identifying informaion", 
        "family members": "Requests patient-identifying informaion", 
        "relatives": "Requests patient-identifying informaion", 
        "which patient": "Asks for individual patient information", 
        "who was": "Asks for individual patient information", 
        "delete": "Requests a destructive database action", 
        "drop": "Requests a destructive database action", 
        "update": "Requests a destructive database action", 
        "insert": "Requests a destructive database action", 
        "ignore policy": "Tries to change rules", 
        "ignore permissions": "Tries to change rules"
    }
    q = question.lower()
    for term, reason in blocked_terms.items():
        if term in q:
            return{
                "allowed": False,
                "reason": reason,
                "matched_term": term,
            }
    return {
        "allowed": True,
        "reason": None,
        "matched_term": None 
    }


def call_ai_hub(system_prompt: str, user_prompt: str) -> str:
    url = f"{os.getenv('AI_HUB_URL')}/generative"
    payload = {
        'ad_object_id': os.getenv('AD_OBJECT_ID'),
        'context': encode_b64(system_prompt),
        'models': ['claude-sonnet-4.6'],
        'prompt': encode_b64(user_prompt)
    }
    headers = {
        "X-API-Key": os.getenv("AI_HUB_API_KEY"),  
        "Content-Type": "application/json"  
    }
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    if data.get('has_error'):
        raise RuntimeError(data.get('error'))
    
    responses = data['data']['generative_responses']
    first = responses[0]
    if first.get('has_error'):
        raise RuntimeError(first.get('response'))
    
    return first['response']


@app.post('/ask')
async def ask(req: AskRequest):
    #Policy Gate
    policy_result = policy_gate(req.question)
    if not policy_result["allowed"]:
        return {
            "question": req.question,
            "policy": policy_result["reason"],
            "denial_reason": policy_result,
            "answer": "Your request cannot be processed because it violates our policy."

        }
    
    #Tools
    router_system_prompt = """
    You are a routing agent. Return ONLY raw JSON. Do not include markdown. Do not include explanations. Do not include code fences. You have two available tools. 
    1: get_table_info(table_name: str) Description: Returns metadata for a mock hospital table, including primary key and description of the table. Use when the user asks about a specific table. When calling get_table_info, normalize the query:
        - Use plural form for words.
        - Remove filler words like "info", "information", "where", "find".
        - Treat related forms as equivalent, e.g. "department" → "departments".
        Example:
        User: Tell me about the encounters table.
        Output:
        {"use_tool": true, "tool_name": "get_table_info", "tool_input": {"table_name": "encounters"}}

    2: search_docs(query: str) Description: Searches tiny, mock hospital documentation for relevant tables. When calling search_docs, normalize the query:
        - Use singular/base words.
        - Remove filler words like "info", "information", "where", "find".
        - Treat related forms as equivalent, e.g. "discharge", "discharges", "discharged" → "discharge".

        Examples:
        User: Where can I find discharge info?
        Output:
        {"use_tool": true, "tool_name": "search_docs", "tool_input": {"query": "discharge"}}

        User: What table has diagnosis information?
        Output:
        {"use_tool": true, "tool_name": "search_docs", "tool_input": {"query": "diagnosis"}}

    Your job is NOT to answer the question. Your job is ONLY to decide whether a tool is needed, and the correct tool. Return ONLY valid JSON. Schema: 
        {
        "use_tool": true or false, 
        "tool_name": string | null, 
        "tool_input": object or dict | null
        }
    """
    
    decision_text = call_ai_hub(system_prompt=router_system_prompt, user_prompt=req.question)
    decision = json.loads(decision_text)

    if decision['use_tool']:
        tool_result = await run_tool(decision['tool_name'], decision['tool_input'])
        answer = generate_final_answer(req.question, tool_result)
        response = {
            'question': req.question,
            "policy": policy_result,
            'decision': decision,
            'tool_result': tool_result,
            'answer': answer
        }
    else:  
        answer = generate_direct_answer(req.question)
        response = {
            'question': req.question,
            "policy": policy_result,
            'decision': decision,
            'answer': answer
        }
    return response


#LLM answer if no tool is needed
def generate_direct_answer(question:str) -> str:
    system_prompt = "You are a helpful assistant. Answer the user's question naturally and concisely, and with proper American English grammar and syntax."
    return call_ai_hub(system_prompt=system_prompt, user_prompt=question)

#Final answer if tool is called
def generate_final_answer(question: str, tool_result) -> str:
    final_system_prompt = "You are a helpful assistant. Answer the user's question naturally and concisely, and with proper American English grammar and syntax. Do not invent any information beyond the tool result."
    final_user_prompt = f"""User question: {question} Tool result: {tool_result}"""
    return call_ai_hub(system_prompt=final_system_prompt, user_prompt=final_user_prompt)


#Run MCP
async def run_tool(tool_name: str, tool_input: dict):
    async with Client(f"{os.getenv('MCP_URL')}") as client:
        result = await client.call_tool(
            tool_name,
            tool_input
        )
        return result.data