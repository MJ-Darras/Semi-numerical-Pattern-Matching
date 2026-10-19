import sys

# this function reads a file and return its content
def read_file(file_path: str) -> list[str]:
    f = open(file_path, 'r')
    line = f.readlines()
    f.close()
    return line

class Node:
    def __init__(self, id:int, leaf_num: int|None = None, parent: "Node | None"= None ) -> None:
        self.id = id
        self.leaf_num = leaf_num
        self.edges: dict[str, "Edge"] = {} # assuming that keys are a single char
        self.suffix_link: Node | None = None
        self.depth = 0
        self.parent = parent
    
    def __str__(self) -> str:
        return f"{self.id}"

    def __repr__(self) -> str:
        return f"n{self.id}"
class Edge:
    # ep stored as list | int since global_end needs to be updated unanimously for edges leading to a leaf
    def __init__(self, sp:int, ep:int | list, destination: Node) -> None:
        self.sp = sp
        self.ep = ep 
        self.destination = destination

    def current_ep(self) -> int:
        if isinstance(self.ep, list):
            return self.ep[0]
        return self.ep

    def length(self) -> int:
        return self.current_ep() - self.sp + 1
    
    def __str__(self) -> str:
        return f"#{self.destination.id} ({self.sp}, {self.ep}) -> {self.destination.leaf_num}"

    def __repr__(self) -> str:
        return f"#{self.destination.id} ({self.sp}, {self.ep}) -> {self.destination.leaf_num}"

class SuffixTree:
    def __init__(self, i_str: str, f_output) -> None:
        self.root = Node(1)
        self.i_str = i_str + "$"
        self.id_counter = 1

        # variables that help in determining location in tree
        self.an: Node = self.root       # active node
        self.ae: Edge | None  = None    # active edge 
        self.al: int = 0                # active length

        self.last_j = 0
        self.global_end = [0]

        self.showstopper = False
        self.tbd_link: Node | None = None

        # variable to export to text file
        self.f_output = f_output

        # variables for calculating LCP
        self.leaves = []
        self.lcp = []
    
    
    def ukkonen(self):
        """
        An implementation of Ukkonen's algorithm for linear time construction of suffix trees.
        Complexity:
        Space -> O(n) 
        Time  -> O(n)
        """
        print("Root Node 1", file= self.f_output)

        # Base case
        self.id_counter += 1
        self.root.edges[self.i_str[0]] = Edge(0, self.global_end, Node(self.id_counter, 0, self.root))
        self.root.suffix_link = self.root

        print("\nPhase 1 starts from Extn 1", file= self.f_output)
        print("    Extn 1 applies Rule 2 (alternate)", file= self.f_output)
        print("    Active Node = Node 1 (suffix link to Node 1); Remainder = EMPTY", file= self.f_output)
        print("        Node 2 created: Leaf node!", file= self.f_output)

        for i in range(1, len(self.i_str)):
            self.global_end[0] += 1

            print(f"\nPhase {i+1} starts from Extn {self.last_j+2}", file= self.f_output)
            for j in range(self.last_j + 1, i + 1):
                # print(f"\ninserting suffix {self.i_str[j:i+1]}\t({j},{i})")

                # skip count down to the extension point
                self.traverse(j, i - 1)

                # Apply the appropriate extension
                self.makeExtension(j, i)

                # skip remaining j's for this phase
                if self.showstopper:
                    self.showstopper = False
                    break

                # Move to next extension i.e. traversing suffix links, or showstopper
                self.moveToNextExtension()
        
        # print("")
        # print(self.global_end)
        return self.root


    # renamed (j , i) to (w , q) 
    # to distinguish that their values are being changed; for better clarity.
    def traverse(self, w:int, q:int):
        """
        Complexity
        Space -> O(1) 
        Time  -> O(1) amortized
        """
        # print(f"following path\t\t({w}, {q})")
        node = self.an

        # add depth to point to the correct character
        w += node.depth

        chars_rem = q - w + 1
        
        # if you reached the required node with no chars remaining, set active edge to None and length to 0 
        if chars_rem == 0:
            self.ae = None
            self.al = 0
            return

        # print(chars_rem, "<- chars rem")

        # while path is not empty
        while chars_rem > 0:
            c = self.i_str[w]
            edge = node.edges.get(c)
            # print(c, "<-", q, w)

            # no edge is found
            if edge is None:
                self.an = node
                self.ae = None
                self.al = 0
                return
            
            # we stop somewhere on or at the end of this edge
            if edge.length() > chars_rem:
                self.an = node
                self.ae = edge
                self.al = chars_rem
                return
            else:
                # skip the edge and move to child node
                w += edge.length()
                chars_rem -= edge.length()
                node = edge.destination
        
        # if loop exited due to chars rem being 0
        self.an = node
        self.ae = None
        self.al = 0


    def makeExtension(self, j:int, i:int):
        """
        Complexity
        Space -> O(1) 
        Time  -> O(1)
        """
        c = self.i_str[i]
        # print(c, i, "<- attempting", self.al)

        rem_start = j + self.an.depth + 1
        rem_end = i
        remainder_str = "EMPTY" if rem_start > rem_end else f"S [{rem_start}...{rem_end}]"
        
        # If we are exactly at a node with no active edge, hence also no length
        if self.ae is None:
            # r3 showstopper
            if c in self.an.edges:
                # print(f"r3 showstopper on '{c}'")
                self.ae = self.an.edges[c]
                self.al = 1 
                # break out of the j loop 
                self.showstopper = True

                # output
                print(f"    Extn {self.last_j+2} applies Rule 3", file= self.f_output)
                print(f"    Active Node = Node {self.an.id} (suffix link to {'Node ' + str(self.an.suffix_link.id) if self.an.suffix_link is not None else ''}); Remainder = {remainder_str}", file= self.f_output)

                # the previous iteration's node is linked with this one's active node
                self.resolveSuffixLinks(self.an)
                return
            
            # r2,c2 create new leaf from node
            else:
                print(f"    Extn {j+1} applies Rule 2 (alternate)", file= self.f_output)
                print(f"    Active Node = Node {self.an.id} (suffix link to {'Node ' + str(self.an.suffix_link.id) if self.an.suffix_link is not None else ''}); Remainder = {remainder_str}", file= self.f_output)
                
                self.id_counter += 1
                self.an.edges[c] = Edge(i, self.global_end, Node(self.id_counter, j, self.an))
                self.last_j = j
                print(f"        Node {self.id_counter} created: Leaf node!", file= self.f_output)

                # print(f"added an edge from {self.an.id} to node {j} | '{c}'")
                
                self.resolveSuffixLinks(self.an)
        else:
        # logic for when you are inside an edge, either split or showstopper
            edge_c = self.i_str[self.ae.sp + self.al]
            insert_c = self.i_str[i]
            
            # char already in edge
            if edge_c == insert_c:
                self.al += 1
                self.showstopper = True

                # output
                print(f"    Extn {self.last_j+2} applies Rule 3", file= self.f_output)
                print(f"    Active Node = Node {self.an.id} (suffix link to {'Node ' + str(self.an.suffix_link.id) if self.an.suffix_link is not None else ''}); Remainder = {remainder_str}", file= self.f_output)

                # the previous iteration's node is linked with this one's active node
                self.resolveSuffixLinks(self.an)

                return
            # r2, c1 add internal node
            else:
                print(f"    Extn {j+1} applies Rule 2 (regular)", file= self.f_output)
                print(f"    Active Node = Node {self.an.id} (suffix link to {'Node ' + str(self.an.suffix_link.id) if self.an.suffix_link is not None else ''}); Remainder = {remainder_str}", file= self.f_output)
                
                self.id_counter += 1
                node_u = Node(self.id_counter, None, self.an)

                print(f"        Node {self.id_counter} created: Internal node!", file= self.f_output)

                # assign depth
                node_u.depth = self.an.depth + self.al

                # resolve the previous link
                self.resolveSuffixLinks(node_u)
                # it is the new internal node's turn to get a link
                self.tbd_link = node_u

                # bottom path update
                node_u.edges[edge_c] = Edge(self.ae.sp + self.al, self.ae.ep, self.ae.destination)

                # new internal node becomes parent
                self.ae.destination.parent = node_u

                # top path update
                self.ae.ep = self.ae.sp + self.al - 1
                self.ae.destination = node_u

                # new leaf branch
                self.id_counter += 1
                node_new = Node(self.id_counter, j, node_u)
                node_u.edges[insert_c] = Edge(i, self.global_end, node_new)

                print(f"        Node {self.id_counter} created: Leaf node!", file= self.f_output)

                # since we did a r2 c1, we update the last j
                self.last_j = j


    def resolveSuffixLinks(self, current_node: Node):
        """
        Complexity
        Space -> O(1) 
        Time  -> O(1)
        """
        # If there is a node from the last iteration waiting for its suffix link
        if self.tbd_link is not None:
            print(f"        Linking Node {self.tbd_link.id} to Node {current_node.id}", file= self.f_output)

            # assign its link to the current active node
            self.tbd_link.suffix_link = current_node
            # reset it to none
            self.tbd_link = None


    def moveToNextExtension(self):
        """
        Complexity
        Space -> O(1) 
        Time  -> O(1)
        """
        # move to link
        if self.an.suffix_link is not None:
            self.an = self.an.suffix_link
        # safety net 
        else:
            self.an = self.root
    
    def LCP(self):
        """
        Complexity
        Space -> O(n) 
        Time  -> O(n * d)
        where:
        n is number of leaves
        d is depth
        """
        # find all leaves and store them in lexicographic order
        self.dfs(self.root, 0)
        self.lcp = [0] * self.leaves.__len__()
        prev = None
        # O(leaves)
        for i in range(1, len(self.leaves)):
            # print(self.leaves[i - 1], self.leaves[i])
            res = self.find_common_ancestor(self.leaves[i - 1], self.leaves[i], prev)
            # store the shared depth value in lcp
            self.lcp[i] = res[0]
            # pass over the precomputed ancestors 
            prev = res[1]

    
    def find_common_ancestor(self, l1: Node, l2: Node, prev_ancestors: list[Node] | None = None):
        """
        A function that finds the depth of the last shared node across two nodes paths

        Complexity
        Space & Time -> O(depth) where depth here refers to the maximum depth a node has in the tree
        """
        shared = 0
        l1_ancestors = []
        l2_ancestors = []
        
        # setup l1 ancestors
        x = l1
        if prev_ancestors is None:
            while True:
                if(x.parent):
                    l1_ancestors.append(x.parent)
                    x = x.parent
                else:
                    break
        else:
            l1_ancestors = prev_ancestors
        
        # setup l2 ancestors
        x = l2
        while True:
            if(x.parent):
                l2_ancestors.append(x.parent)
                x = x.parent
            else:
                break
        
        # Compare ancestors
        for i in range(min(len(l1_ancestors), len(l2_ancestors))):
            if(l1_ancestors[-(i+1)] == l2_ancestors[-(i+1)]):
                # shared ancestor's depth
                shared = l1_ancestors[-(i+1)].depth
            else:
                break

        return (shared, l2_ancestors)
    
    def dfs(self, node: Node, depth: int):
        """
        Complexity:
        Space -> O(n) 
        Time  -> O(n log x)
        where:
        x is alphabet.
        n is number of edges. 
        """
        for k in sorted(node.edges.keys()):
            e = node.edges.get(k)
            if e is not None:
                if(e.destination.leaf_num is not None):
                    self.leaves.append(e.destination)
                else:
                    self.dfs(e.destination, depth + 1)


if __name__ == '__main__':
    #retrieve the file paths from the commandline arguments
    _, filename1 = sys.argv
    
    # since we know the program takes two arguments
    # print("First argument : ", filename1)

    file1content = read_file(filename1)
    # print("\nContent of first file : ", file1content)

    with open("runloga2q1.txt", "w") as f_output:
        st = SuffixTree(file1content[0], f_output) 
        st.ukkonen()

    st.LCP()
    
    with open("output_a2q1.txt", "w") as f:
        f.write("\n".join(str(v) for v in st.lcp))