"""Assignment 7 scaffold: MiniServe's uncached manual greedy decoder."""
import mlx.core as core
from torch._dynamo.utils import _breakpoint_for_c_dynamo

# TODO: Select `[batch, vocabulary]` logits from the final sequence position.
def select_last_position_logits(logits):
    """Select `[batch, vocabulary]` logits from the final sequence position."""
    logit = logits[:, -1, :]
    
    if (logits.ndim != 3):
        raise ValueError(f"needed shape [B, T, V] but got {logits.shape} instead")
    
    return logit


# TODO: Choose the maximum-logit token ID without using a generation helper.
def greedy_next_token(logits):
    """Choose the maximum-logit token ID without using a generation helper."""
    # what the, greedy decoding is just argmax(logits) but for the V axis
    
    return core.argmax(logits, axis=-1)


# TODO: Create the next full-sequence input by appending one token on sequence axis.
def append_token(token_ids, next_token_id):
    """Create the next full-sequence input by appending one token on sequence axis."""
    next_token_id = core.expand_dims(next_token_id, axis=1)
    #so here the token_ids is rank 2 because its [1, 36], meaning [[3123123, 323423, ...]]
    #but next_token_id is only rank 1 [9707] so we have to make it rank 2 by just rehsaping it into [[9707]] to add after the 36th token
    
    appended = core.concatenate([token_ids, next_token_id], axis=1) #after appension, we now have the new token_ids.shape to be [1, 37], axis=1 bc we only wanna concat the second part
    
    return appended


# TODO: Yield one structured step after each full-sequence model forward pass.
def uncached_generate_steps(adapter, prompt_token_ids, max_new_tokens):
    """Yield one structured step after each full-sequence model forward pass."""
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
    


# TODO: Own encode-loop-stop-decode control flow and return text plus token trace.
def generate_text(adapter, prompt, max_new_tokens):
    """Own encode-loop-stop-decode control flow and return text plus token trace."""
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
        


# TODO: Parse CLI arguments and run one deterministic prompt through MiniServe.
def main():
    """Parse CLI arguments and run one deterministic prompt through MiniServe."""
    
    

if __name__ == "__main__":
    main()
