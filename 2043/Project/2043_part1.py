import sys
import math

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

    total_weight=0.0
    for v in range(1,n):
        u=parent[v]
        ux,uy=points[u]
        vx,vy=points[v]
        dx=ux-vx
        dy=uy-vy
        total_weight+=math.sqrt(dx**2+dy**2)
    return parent,total_weight

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
    parent,total_weight=prim_mst(n,points)
    re=[]
    for v in range(1,n):
        u=parent[v]
        re.append(f"{u} {v}")
    re.append(str(total_weight))
    sys.stdout.write("\n".join(re)+"\n")

if __name__ == "__main__":
    main()