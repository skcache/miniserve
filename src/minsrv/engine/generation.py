import mlx.core as core
import argparse
from minsrv.models.adapter import ModelAdapter


def select_last_position_logits(logits):
    logit = logits[:, -1, :]
    
    if (logits.ndim != 3):
        raise ValueError(f"needed shape [B, T, V] but got {logits.shape} instead")
    
    return logit


def greedy_next_token(logits):
    # what the, greedy decoding is just argmax(logits) but for the V axis
    
    return core.argmax(logits, axis=-1)


def append_token(token_ids, next_token_id):
    next_token_id = core.expand_dims(next_token_id, axis=1)
    #so here the token_ids is rank 2 because its [1, 36], meaning [[3123123, 323423, ...]]
    #but next_token_id is only rank 1 [9707] so we have to make it rank 2 by just rehsaping it into [[9707]] to add after the 36th token
    
    appended = core.concatenate([token_ids, next_token_id], axis=1) #after appension, we now have the new token_ids.shape to be [1, 37], axis=1 bc we only wanna concat the second part
    
    return appended


def uncached_generate_steps(adapter, prompt_token_ids, max_new_tokens):
    growingSeq = prompt_token_ids
    
    for i in range(max_new_tokens):
        fwdOut = adapter.forward(growingSeq, cache=None)
        logits = fwdOut["logits"]
        
        lastPos = select_last_position_logits(logits)
        next_token_ids = greedy_next_token(lastPos)
        
        core.eval(next_token_ids) #force the selected token 
        
        next = next_token_ids[0].item()
        growingSeq = append_token(growingSeq, next_token_ids)
        
        core.eval(growingSeq) #prevent lazy graph accumulation
        
        eos_token_ids = adapter.tokenizer.eos_token_ids
        is_eos = next in eos_token_ids
        
        yield {
            "step": i + 1,
            "next_token_id": next,
            "sequence_length": growingSeq.shape,
            "token_ids": growingSeq,
            "is_eos": is_eos,
        }
        
        #instead of return we just yield so function doesnt get destroyed and local variables are stored
        
        if is_eos:
            break
    


def generate_text(adapter, prompt, max_new_tokens):
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    prompt_token_ids = adapter.encode_chat_prompt(messages)
    prompt_length = prompt_token_ids.shape[1]
    
    trace = []
    final_token_ids = prompt_token_ids
    
    for step in uncached_generate_steps(adapter, prompt_token_ids, max_new_tokens):
        trace.append(step)
        final_token_ids = step["token_ids"]
    
    generated_token_ids = final_token_ids[:, prompt_length:] #here we remove the original prompt to seperate the input and output
    generated_text = adapter.decode_tokens(generated_token_ids)
    
    return {
        "text": generated_text,
        "generated_token_ids": generated_token_ids,
        "trace": trace,
    }
        


def main():
    parser = argparse.ArgumentParser(
        description="MiniServe manual greedy decoder"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default="What is the capital of France?",
    )

    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=16,
    )

    args = parser.parse_args()

    adapter = ModelAdapter.load(
        model_id="mlx-community/Qwen2.5-0.5B-Instruct-4bit",
        model_revision="a5339a4",
    )

    result = generate_text(
        adapter,
        args.prompt,
        args.max_new_tokens,
    )

    print("Prompt:")
    print(args.prompt)

    print("\nGenerated:")
    print(result["text"])

    print("\nToken trace:")
    for step in result["trace"]:
        print(
            f"step={step['step']} "
            f"token={step['next_token_id']} "
            f"length={step['sequence_length']} "
            f"eos={step['is_eos']}"
        )

    
if __name__ == "__main__":
    main()
