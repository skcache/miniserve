// MiniServe — Issue #23: Native Model and Tokenizer Adapter
//
// Role: compilation unit reserved for the model/tokenizer boundary.
// Responsibilities: implement only the contract declared in adapter.hpp.
// Does NOT own: generation, cache policy, batching, or scheduling.
// Key invariants: one model load; [B,T] tokens; [B,T,V] logits.
// Evidence required: metadata, shape, and Python parity tests.
// Implementation: TODO — Issue #23

#include "miniserve/model/adapter.hpp"

namespace miniserve::model {
// TODO — Issue #23: learner implementation belongs here.
}
