import json
from fastapi import FastAPI

from model_server.schemas import AskRequest
from model_server.policy import policy_gate
from model_server.call_ai_hub import call_ai_hub
from model_server.prompts import (
    ROUTER_SYSTEM_PROMPT,
    DIRECT_ANSWER_PROMPT,
    FINAL_ANSWER_PROMPT,
)
from model_server.tools_client import run_tool


app = FastAPI(title='Model Server')


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
    
    #Router LLM Node
    decision_text = call_ai_hub(system_prompt=ROUTER_SYSTEM_PROMPT, user_prompt=req.question)
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
    return call_ai_hub(system_prompt=DIRECT_ANSWER_PROMPT, user_prompt=question)

#Final answer if tool is called. Gives an answer based on the tool's output, which is passed as the prompt. 
def generate_final_answer(question: str, tool_result) -> str:
    final_user_prompt = f"""
    User question: {question} 
    Tool result: {tool_result}
    """
    return call_ai_hub(system_prompt=FINAL_ANSWER_PROMPT, user_prompt=final_user_prompt)


