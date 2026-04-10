import java.util.*;

class Graph {
    private Map<String, List<String>> graph;
    private List<String> path;
    private int explored;

    public Graph() {
        graph = new HashMap<>();
        path = new ArrayList<>();
        explored = 0;
    }

    public void addEdge(String node, List<String> neighbors) {
        graph.put(node, neighbors);
    }

    public void depthFirstSearch(String start, String finish) {
        Set<String> visited = new HashSet<>();
        Deque<String> stack = new ArrayDeque<>();

        stack.push(start);

        while (!stack.isEmpty()) {
            String current = stack.pop();

            if (!visited.contains(current)) {
                visited.add(current);
                path.add(current);
                explored++;

                if (current.equals(finish)) {
                    break;
                }

                List<String> neighbors = new ArrayList<>(graph.get(current));
                Collections.reverse(neighbors); // supaya urutan DFS tetap sama

                for (String next : neighbors) {
                    if (!visited.contains(next)) {
                        stack.push(next);
                    }
                }
            }
        }
    }

    public void printResult() {
        System.out.println("Path : " + String.join(" -> ", path));
        System.out.println("Explored node : " + explored);
    }
}

public class depth_first_search {
    public static void main(String[] args) {
        Graph g = new Graph();

        g.addEdge("A", Arrays.asList("B", "C"));
        g.addEdge("B", Arrays.asList("A", "D", "E"));
        g.addEdge("C", Arrays.asList("A", "E"));
        g.addEdge("D", Arrays.asList("B"));
        g.addEdge("E", Arrays.asList("B", "C", "F"));
        g.addEdge("F", Arrays.asList("E"));

        g.depthFirstSearch("A", "F");
        g.printResult();
    }
}