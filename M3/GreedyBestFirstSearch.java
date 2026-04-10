import java.util.*;

class GreedySearch {

    static class Node {
        String name;
        int heuristic;

        Node(String name, int heuristic) {
            this.name = name;
            this.heuristic = heuristic;
        }
    }

    private Map<String, List<Node>> graph = new HashMap<>();

    public void addEdge(String node, List<Node> neighbors) {
        graph.put(node, neighbors);
    }

    public void greedyBestFirst(String start, String goal) {

        Set<String> visited = new HashSet<>();
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(n -> n.heuristic));

        List<String> path = new ArrayList<>();
        int explored = 0;

        pq.add(new Node(start, 0));

        while (!pq.isEmpty()) {
            Node current = pq.poll();

            if (!visited.contains(current.name)) {
                visited.add(current.name);
                path.add(current.name);
                explored++;

                if (current.name.equals(goal)) {
                    break;
                }

                for (Node neighbor : graph.get(current.name)) {
                    if (!visited.contains(neighbor.name)) {
                        pq.add(neighbor);
                    }
                }
            }
        }

        System.out.println("Path found : " + String.join(" -> ", path));
        System.out.println("Nodes explored: " + explored);
    }
}

public class GreedyBestFirstSearch {
    public static void main(String[] args) {

        GreedySearch g = new GreedySearch();

        g.addEdge("A", Arrays.asList(new GreedySearch.Node("B", 3), new GreedySearch.Node("C", 2)));
        g.addEdge("B", Arrays.asList(new GreedySearch.Node("D", 4), new GreedySearch.Node("E", 1)));
        g.addEdge("C", Arrays.asList(new GreedySearch.Node("E", 1)));
        g.addEdge("D", new ArrayList<>());
        g.addEdge("E", Arrays.asList(new GreedySearch.Node("F", 0)));
        g.addEdge("F", new ArrayList<>());

        g.greedyBestFirst("A", "F");
    }
}