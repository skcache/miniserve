#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace miniserve {

using TokenId = std::int32_t;

struct TensorShape {
    std::vector<std::size_t> dimensions;
};

struct ModelIdentity {
    std::string model_id;
    std::string revision;
};

}  // namespace miniserve
