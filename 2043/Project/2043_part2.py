import sys
import math
sys.setrecursionlimit(20000)    # Just in case the MST is very deep

def prim_mst(n,points):
    INF=float("inf")
    dist=[INF]*n    # Store squared distance to reduce calculation cost
    parent=[-1]*n
    visited=[False]*n
    dist[0]=0.0
    for _ in range(n):
        u=-1
        min_dist=INF
        for i in range(n):
            if not visited[i] and dist[i]<min_dist:
                min_dist=dist[i]
                u=i
        visited[u]=True
        ux,uy=points[u]
        for v in range(n):
            if not visited[v]:
                vx,vy=points[v]
                dx=ux-vx
                dy=uy-vy
                w2=dx**2+dy**2
                if w2<dist[v]:
                    dist[v]=w2
                    parent[v]=u
    return parent

def build_adj(n,parent):
    adj=[[] for _ in range(n)]
    for v in range(1,n):
        u=parent[v]
        adj[u].append(v)
        adj[v].append(u)
    return adj

def dfs(u,par,adj,tour):
    tour.append(u)
    for v in adj[u]:
        if v!=par:
            dfs(v,u,adj,tour)
            tour.append(u)

def compute_euler_tour(adj,start=0):
    euler_tour=[]
    dfs(start,-1,adj,euler_tour)
    return euler_tour

def shortcutting(n,euler_tour):
    tsp_tour=[]
    visited=[False]*n
    for v in euler_tour:
        if not visited[v]:
            visited[v]=True
            tsp_tour.append(v)
    return tsp_tour

def tsp_length(n,tsp_tour,points):
    total_length=0.0
    for i in range(n):
        u=tsp_tour[i]
        v=tsp_tour[(i+1)%n]
        ux,uy=points[u]
        vx,vy=points[v]
        dx=ux-vx
        dy=uy-vy
        total_length+=math.sqrt(dx**2+dy**2)
    return total_length

def read_data():
    data=sys.stdin.read().split()
    it=iter(data)
    n=int(next(it))
    points=[]
    for _ in range(n):
        x=float(next(it))
        y=float(next(it))
        points.append((x,y))
    return n,points

def main():
    n,points=read_data()
    parent=prim_mst(n,points)
    adj=build_adj(n,parent)
    euler_tour=compute_euler_tour(adj,start=0)
    tsp_tour=shortcutting(n,euler_tour)
    total_length=tsp_length(n,tsp_tour,points)
    tsp_tour.append(tsp_tour[0])
    tour=" ".join(str(v) for v in tsp_tour)
    sys.stdout.write(tour+"\n")
    sys.stdout.write(str(total_length)+"\n")

if __name__ == "__main__":
    main()