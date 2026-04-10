import java.util.*;

public class BFSExample {

    static Map<String, List<String>> graph = new HashMap<>();

    public static void main(String[] args) {

        // Inisialisasi graph
        graph.put("A", Arrays.asList("B", "C"));
        graph.put("B", Arrays.asList("A", "D", "E"));
        graph.put("C", Arrays.asList("A", "E"));
        graph.put("D", Arrays.asList("B"));
        graph.put("E", Arrays.asList("B", "C", "F"));
        graph.put("F", new ArrayList<>());

        bfs("A", "F");
    }

    public static void bfs(String start, String goal) {

        Queue<List<String>> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();

        queue.add(Arrays.asList(start));
        int nodesExplored = 0;

        while (!queue.isEmpty()) {
            List<String> path = queue.poll();
            String node = path.get(path.size() - 1);

            if (!visited.contains(node)) {
                visited.add(node);
                nodesExplored++;

                if (node.equals(goal)) {
                    System.out.print("Path found : ");
                    for (int i = 0; i < path.size(); i++) {
                        System.out.print(path.get(i));
                        if (i < path.size() - 1) {
                            System.out.print(" -> ");
                        }
                    }
                    System.out.println();
                    System.out.println("Nodes explored : " + nodesExplored);
                    return;
                }

                for (String neighbor : graph.get(node)) {
                    List<String> newPath = new ArrayList<>(path);
                    newPath.add(neighbor);
                    queue.add(newPath);
                }
            }
        }
    }
}