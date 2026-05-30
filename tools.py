import angr
import claripy


def explore_path(binary_path):

    proj = angr.Project(
        binary_path,
        auto_load_libs=False
    )

    flag = claripy.BVS("flag", 5 * 8)

    state = proj.factory.full_init_state(
        args=[binary_path],
        stdin=flag
    )

    for i in range(4):
        state.solver.add(flag.get_byte(i) >= 0x20)
        state.solver.add(flag.get_byte(i) <= 0x7e)

    state.solver.add(flag.get_byte(4) == 10)

    simgr = proj.factory.simgr(state)

    simgr.explore(
        find=lambda s:
            b"Success! Flag is found." in s.posix.dumps(1),

        avoid=lambda s:
            b"trapped" in s.posix.dumps(1)
    )

    return simgr


def solve_input(simgr):

    if len(simgr.found) == 0:
        return None

    found = simgr.found[0]

    return found.posix.dumps(0)
