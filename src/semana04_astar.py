import heapq


GRID = [
    ".....",
    ".###.",
    "...#.",
    ".#...",
    ".....",
]

START = (0, 0)
GOAL = (4, 4)


def h(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(node):
    r, c = node

    for dr, dc in (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ):
        nr = r + dr
        nc = c + dc

        if (
            0 <= nr < len(GRID)
            and 0 <= nc < len(GRID[0])
            and GRID[nr][nc] != "#"
        ):
            yield (nr, nc)


def astar(start, goal):
    frontier = [(0, start)]

    came_from = {
        start: None
    }

    cost = {
        start: 0
    }

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for nxt in neighbors(current):
            new_cost = cost[current] + 1

            if (
                nxt not in cost
                or new_cost < cost[nxt]
            ):
                cost[nxt] = new_cost

                priority = (
                    new_cost
                    + h(nxt, goal)
                )

                heapq.heappush(
                    frontier,
                    (
                        priority,
                        nxt
                    )
                )

                came_from[nxt] = current

    if goal not in came_from:
        return None

    path = []
    cur = goal

    while cur is not None:
        path.append(cur)
        cur = came_from[cur]

    return list(
        reversed(path)
    )


path = astar(
    START,
    GOAL
)

print(
    "Ruta:",
    path
)

print(
    "Costo:",
    len(path) - 1
    if path
    else None
)