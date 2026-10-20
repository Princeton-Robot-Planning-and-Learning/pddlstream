// Compile with -std=c++11 and run to check the vendored optional reference fix.
#include "../pddlstream/_downward/src/search/ext/optional.hh"
#include <cassert>
#include <memory>

struct NonCopyable {
    explicit NonCopyable(int value) : value(value) {}
    NonCopyable(const NonCopyable &) = delete;
    NonCopyable &operator=(const NonCopyable &) = delete;
    int value;
};

int main() {
    NonCopyable first(1), second(2);
    tl::optional<NonCopyable &> ref;
    assert(!ref);
    assert(std::addressof(ref.emplace(first)) == std::addressof(first));
    ref->value = 3;
    assert(first.value == 3);
    assert(std::addressof(ref.emplace(second)) == std::addressof(second));
    assert(first.value == 3); // Rebinding must not assign to the previous object.
    ref.reset();
    assert(!ref);
    ref.emplace(first);

    tl::optional<const NonCopyable &> const_ref;
    const_ref.emplace(first);
    assert(std::addressof(*const_ref) == std::addressof(first));

    // Owned optionals must still construct and own their values normally.
    tl::optional<NonCopyable> owned;
    assert(owned.emplace(7).value == 7);

#ifdef TEST_REJECT_TEMPORARY
    // Compiling with this macro must fail instead of accepting a dangling ref.
    const_ref.emplace(NonCopyable(9));
#endif
}
