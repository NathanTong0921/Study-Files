# lab 2
# Q2
# def closest_search(arr,tar):
#     left=0
#     right=len(arr)-1
#     while left<=right:
#         mid=(left+right)//2
#         if arr[mid]>tar:
#             right=mid-1
#         elif arr[mid]<tar:
#             left=mid+1
#         else:
#             return mid
#     注意handle边界
#     if right<0:
#         return 0
#     if left>len(arr)-1:
#         return len(arr)-1
#     rhs_margin=abs(arr[left]-tar)
#     lhs_margin=abs(arr[right]-tar)
#     if rhs_margin<=lhs_margin:    # 注意“最近”的判断条件
#         return left
#     else:
#         return right  
# a=int(input())
# b=input().split()
# c=[int(x) for x in b] 
# for i in range (a):
#     c.append(int(b[i]))
# t=int(input())
# print(closest_search(c,t))

# lab 3
# Q1
# def bubble_sort(arr):
#     n=len(arr)
#     if n==0:
#         print("Swaps: 0, First: N/A, Last: N/A")
#         return
#     swap=0
#     for i in range (n-1):
#         swapped=False
#         for j in range (n-1-i):
#             if arr[j]>arr[j+1]:
#                 arr[j],arr[j+1]=arr[j+1],arr[j]
#                 swap+=1
#                 swapped=True
#         if swapped==False:
#             break
#     # 注意输出方式
#     print(f"Swaps: {swap}, First: {arr[0]}, Last: {arr[n-1]}")
#
# Q3
# def selection_sort(n,arr):
#     swaps=0
#     for i in range (n-1):
#         min_index=i
#         for j in range (i+1,n):
#             if arr[j]<arr[min_index]:
#                 min_index=j
#         arr[min_index],arr[i]=arr[i],arr[min_index]
#         if i!=min_index:
#             swaps+=1
#     print(*arr)   # *可以让输出数组不带中括号
#     print(swaps)
# a=int(input())
# if a==0:      # n=0时没有第二行输入，会RE
#     print()   # 打印空行
# else:
# 	b=input().split()
# 	c=[int(x) for x in b]
# 	selection_sort(a,c)

# lab 4
# Q3
# 思路：[-k,k]映射到[0,2k]，输出时再-k
# def counting_sort_with_neg(arr,k):
#     # k=max(abs(x) for x in arr)
#     U=2*k+1
#     counts=[0]*U
#     for i in arr:
#         counts[i+k]+=1
#     re=[]
#     for j in range(U):
#         while counts[j]>0:
#             re.append(j-k)
#             counts[j]-=1
#     return re
# l1=input().split()
# l11=[int(x) for x in l1]
# n=l11[0]
# k=l11[1]
# if n==0:
#     print()
# else:
#     l2=input().split()
#     arr=[int(x) for x in l2]
#     print(*counting_sort_with_neg(arr,k))

# lab 6
# Q1 1046
"""
class max_tree:
    def __init__(self,arr=None):
        self.a=[]
        if arr:
            self.a=list(arr)
            self.build_heap()
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            if self.a[parent]>self.a[i]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            biggest=i
            if left<n and self.a[biggest]<self.a[left]:
                biggest=left
            if right<n and self.a[biggest]<self.a[right]:
                biggest=right
            if biggest==i:
                break
            self.a[biggest],self.a[i]=self.a[i],self.a[biggest]
            i=biggest
    def build_heap(self):
        n=len(self.a)
        for i in range((n-2)//2,-1,-1):
            self.heapify_down(i)
    def insert(self,val):
        self.a.append(val)
        self.heapify_up(len(self.a)-1)
    def pop_max(self):
        n=len(self.a)-1
        self.a[0],self.a[n]=self.a[n],self.a[0]
        max_val=self.a.pop()
        self.heapify_down(0)
        return max_val
    def length(self):
        return len(self.a)
def last_stone_weight(heap):
    while heap.length()>1:
        y=heap.pop_max()
        x=heap.pop_max()
        if x!=y:
            heap.insert(y-x)
    if heap.length()==1:
        return heap.a[0]
    else:
        return 0
n=int(input())
a=input().split()
arr=[int(x) for x in a]
heap=max_tree(arr)
print(last_stone_weight(heap))
"""
# Q2 506
"""
class MaxHeap:
    def __init__(self,arr=None):
        self.a=[]
        if arr:
            self.a=list(arr)
            self.build_heap()
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            if self.a[parent][0]>self.a[i][0]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            biggest=i
            if left<n and self.a[biggest][0]<self.a[left][0]:
                biggest=left
            if right<n and self.a[biggest][0]<self.a[right][0]:
                biggest=right
            if biggest==i:
                break
            self.a[i],self.a[biggest]=self.a[biggest],self.a[i]
            i=biggest            
    def build_heap(self):
        n=len(self.a)
        for i in range((n-2)//2,-1,-1):
            self.heapify_down(i)
    def pop_max(self):
        self.a[0],self.a[-1]=self.a[-1],self.a[0]
        max_val=self.a.pop()
        if self.a:
            self.heapify_down(0)
        return max_val
n=int(input())
a=input().split()
b=[int(x) for x in a]
arr=[(b[i],i) for i in range(len(b))]
heap=MaxHeap(arr)
re=[""]*len(arr)
i=1
while i<=len(arr):
    pair=heap.pop_max()
    if i==1:
        re[pair[1]]="Gold Medal"
    elif i==2:
        re[pair[1]]="Silver Medal"
    elif i==3:
        re[pair[1]]="Bronze Medal"
    else:
        re[pair[1]]=str(i)
    i+=1
print(*re)
"""

# lab 7
# Q1
"""
class Node:
    def __init__(self,val):
        self.left=None
        self.right=None
        self.val=val
class BST:
    def __init__(self,arr):
        self.root=None
        self.build(arr)
    def build(self,arr):
        for x in arr:
            self.insert(x)
    def insert(self,x):
        if self.root is None:
            self.root=Node(x)
            return
        cur=self.root
        while True:
            if x<cur.val:
                if cur.left is None:
                    cur.left=Node(x)
                    return
                cur=cur.left
            else:
                if cur.right is None:
                    cur.right=Node(x)
                    return
                cur=cur.right
    def in_order(self,node,re):
        if node:
            self.in_order(node.left,re)
            re.append(node.val)
            self.in_order(node.right,re)
        return re
n=int(input())
a=input().split()
arr=[int(x) for x in a]
bst=BST(arr)
ans=[]
bst.in_order(bst.root,ans)
print(*ans)
"""
# Q2
"""
class Node:
    def __init__(self,val):
        self.left=None
        self.right=None
        self.val=val
class BST:
    def __init__(self,arr):
        self.root=None
        self.build(arr)
    def build(self,arr):
        for x in arr:
            self.insert(x)
    def insert(self,x):
        if self.root is None:
            self.root=Node(x)
            return 
        cur=self.root
        while True:
            if x<cur.val:
                if cur.left is None:
                    cur.left=Node(x)
                    return
                cur=cur.left
            else:
                if cur.right is None:
                    cur.right=Node(x)
                    return
                cur=cur.right
    def search(self,x):
        cur=self.root
        while True:
            if x<cur.val:
                if cur.left is None:
                    return []
                cur=cur.left
            elif x>cur.val:
                if cur.right is None:
                    return []
                cur=cur.right
            else:
                re=[]
                return self.pre_order(cur,re)
    def pre_order(self,node,re):
        if node:
            re.append(node.val)
            self.pre_order(node.left,re)
            self.pre_order(node.right,re)
        return re
n=input()
a=input().split()
arr=[int(x) for x in a]
v=int(input())
bst=BST(arr)
ans=bst.search(v)
if ans:
    print(*ans)
else:
    print("NULL")
"""
# Q3
"""class Node:
    def __init__(self,val):
        self.val=val
        self.left=None
        self.right=None
        self.h=0    # 单节点高度为0
class avl_tree:
    def __init__(self,arr):
        self.root=None
        self.build(arr)
    def build(self,arr):
        # 前序遍历顺序恰好等价于插入顺序
        # 从空树按前序顺序插入, 得到的树就是原来的 BST
        for x in arr:
            self.insert(x)
    def insert(self,x):
        if self.root is None:
            self.root=Node(x)
            return
        cur=self.root
        while True:
            if x<cur.val:
                if cur.left is None:
                    cur.left=Node(x)
                    return
                cur=cur.left
            else:
                if cur.right is None:
                    cur.right=Node(x)
                    return
                cur=cur.right
    def height(self,t):
        return t.h if t else -1
    def update(self,t):
        if t:
            t.h=1+max(self.height(t.left),self.height(t.right))
    def balance_factor(self,t):
        return self.height(t.left)-self.height(t.right) if t else 0
    def right_rotate(self,t):
        #      t                x
        #     / \              / \
        #    x   C   ===>     A   t
        #   / \                  / \
        #  A   B                B   C
        x=t.left
        B=x.right
        x.right=t
        t.left=B
        # 先低后高的顺序更新高度
        self.update(t)
        self.update(x)
        return x    # 返回新根
    def left_rotate(self,t):
        #    t                    y
        #   / \                  / \
        #  A   y      ===>      t   C
        #     / \              / \
        #    B   C            A   B
        y=t.right
        B=y.left
        y.left=t
        t.right=B
        self.update(t)
        self.update(y)
        return y
    def rebalance(self,t):
        if not t:
            return None
        while True:
            self.update(t)
            bf=self.balance_factor(t)
            if bf>1:
                if self.balance_factor(t.left)<0:
                    t.left=self.left_rotate(t.left)
                t=self.right_rotate(t)
            elif bf<-1:
                if self.balance_factor(t.right)>0:
                    t.right=self.right_rotate(t.right)
                t=self.left_rotate(t)
            else:
                self.update(t)
                return t
    def balance(self,t):
        if not t:
            return None
        t.left=self.balance(t.left)
        t.right=self.balance(t.right)
        return self.rebalance(t)
    def pre_order(self,node,re):
        if node:
            re.append(node.val)
            self.pre_order(node.left,re)
            self.pre_order(node.right,re)
        return re
n=int(input())
a=input().split()
arr=[int(x) for x in a]
tree=avl_tree(arr)
tree.root=tree.balance(tree.root)
ans=[]
ans=tree.pre_order(tree.root,ans)
print(*ans)
"""

# lab 9
# Q1
"""
1D
def subsetSum(n,t,arr):
    dp=[False]*(t+1)
    dp[0]=True
    for v in arr:
        for s in range(t,v-1,-1):
            if dp[s-v]:
                dp[s]=True
    return "YES" if dp[t] else "NO"
l=input().split()
n,t=int(l[0]),int(l[1])
a=input().split()
arr=[int(x) for x in a]
print(subsetSum(n,t,arr))

2D
def subsetSum(n,t,arr):
    dp=[[False]*(t+1) for _ in range(n+1)]
    dp[0][0]=True
    for i in range(1,n+1):
        v=arr[i-1]
        for s in range(t+1):
            dp[i][s]=dp[i-1][s]
            if s>=v and dp[i-1][s-v]:
                dp[i][s]=True
    return "YES" if dp[n][t] else "NO"
l=input().split()
n,t=int(l[0]),int(l[1])
a=input().split()
arr=[int(x) for x in a]
print(subsetSum(n,t,arr))
"""
# Q2
"""
def LCS(s1,s2):
    n,m=len(s1),len(s2)
    dp=[[0]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1):
        for j in range(1,m+1):
            if s1[i-1]==s2[j-1]:
                dp[i][j]=1+dp[i-1][j-1]
            else:
                dp[i][j]=max(dp[i-1][j],dp[i][j-1])
    return dp[n][m]     # 注意return dp[n][m]
s1=input()
s2=input()
print(LCS(s1,s2))
"""
# Q3
"""
def BP(n,nums):
    total=sum(nums) 
    if total%2==1:
        return 'NO'
    t=total//2
    dp=[False]*(t+1)
    dp[0]=True
    for v in nums:
        for s in range(t,v-1,-1):
            if dp[s-v]:
                dp[s]=True
    return "YES" if dp[t] else "NO"
n=input()
a=input().split()
arr=[int(x) for x in a]
print(BP(n,arr))
"""

# lab 10
# Q1
"""
def activity_selection(intervals,r):
    new_intervals=[(s,e+r) for s,e in intervals]
    new_intervals.sort(key=lambda x:x[1])
    count=0
    last_end=-float('inf')
    for s,e in new_intervals:
        if s>=last_end:
            last_end=e
            count+=1
    return count
n,r=map(int,input().split())
intervals=[]
for _ in range(n):
    s,e=map(int,input().split())
    intervals.append((s,e))
print(activity_selection(intervals,r))
"""
# Q2
"""
class UnionFind:
    def __init__(self,n):
        self.parent=list(range(n+1))
        self.rank=[0]*(n+1)
    def find(self,x):
        if self.parent[x]!=x:
            self.parent[x]=self.find(self.parent[x])
        return self.parent[x]
    def union(self,a,b):
        pa,pb=self.find(a),self.find(b)
        if pa==pb:
            return False
        if self.rank[pa]<self.rank[pb]:
            self.parent[pa]=pb
        elif self.rank[pa]>self.rank[pb]:
            self.parent[pb]=pa
        else:
            self.parent[pb]=pa
            self.rank[pa]+=1
        return True

def mst_kruskal(n,edges):
    edges.sort(key=lambda x:x[2])
    uf=UnionFind(n)
    cost=0
    used=0
    for u,v,w in edges:
        if uf.union(u,v):
            cost+=w
            used+=1
            if used==n-1:   # n节点树要n-1条边
                break
    if used<n-1:
        return None
    return cost

n,m=map(int,input().split())
edges=[]
for _ in range(m):
    u,v,w=map(int,input().split())
    edges.append((u,v,w))
ans=mst_kruskal(n,edges)
if ans is None:
    print("IMPOSSIBLE")
else:
    print(ans)

    
import heapq
def prim(n,graph,start=0):
    visited=[False]*n
    heap=[(0,start)]
    mst_weight=0
    count=0
    while heap and count<n:
        w,u=heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u]=True
        mst_weight+=w
        count+=1
        for v,weight in graph[u]:
            if not visited[v]:
                heapq.heappush(heap,(weight,v))
    if count<n:
        return None
    return mst_weight

n,m=map(int,input().split())
graph=[[] for _ in range(n)]
for _ in range(m):
    u,v,w=map(int,input().split())
    graph[u].append((v,w))
    graph[v].append((u,w))
print(prim(n,graph))
"""

# lab 11
# Q1
"""
from collections import deque
def bfs(start,graph):
    q=deque()
    q.append(start)
    visited=[False]*len(graph)
    visited[start]=True
    re=[]
    while q:
        u=q.popleft()
        re.append(u)
        for v in graph[u]:
            if not visited[v]:
                q.append(v)
                visited[v]=True
    return re

n,m,start=map(int,input().split())
graph=[[] for _ in range(n)]
for _ in range(m):
    u,v=map(int,input().split())
    graph[u].append(v)
    graph[v].append(u)
print(*bfs(start,graph))
"""
# Q2
"""
import heapq
INF=float('inf')
def dijkstra(start,graph):
    n=len(graph)
    dist=[INF]*n
    parent=[-1]*n
    dist[start]=0
    pq=[]
    heapq.heappush(pq,(0,start))
    while pq:
        cur_dist,u=heapq.heappop(pq)
        if cur_dist>dist[u]:
            continue
        for v,w in graph[u]:
            if dist[u]+w<dist[v]:
                dist[v]=dist[u]+w
                parent[v]=u
                heapq.heappush(pq,(dist[v],v))
    return dist,parent
def get_path(start,end,parent):
    path=[]
    cur=end
    while cur!=-1:
        path.append(cur)
        if cur==start:
            break
        cur=parent[cur]
    if not path or path[-1]!=start:
        return []
    path.reverse()  # 这是原地修改，不返回值
    return path
n,m,start,t=map(int,input().split())
graph=[[] for _ in range(n)]
for _ in range(m):
    u,v,w=map(int,input().split())
    graph[u].append((v,w))
dist,parent=dijkstra(start,graph)
dist_out=["INF" if d==INF else str(d) for d in dist]
print(" ".join(dist_out))
print(*get_path(start,t,parent)) if get_path(start,t,parent) else print("NO PATH")
"""




# Exam A
# Q2 
# 考点：二分查找
# def binary_search_index(arr):
#     l=0
#     r=len(arr)-1
#     while l<=r:
#         mid=(l+r)//2
#         if arr[mid]==mid:
#             return mid
#         elif arr[mid]>mid:
#             r=mid-1
#         else:
#             l=mid+1
#     return -1
# a=int(input())
# if a==0:
#     print(-1)
# else:
#     b=input().split()
#     c=[int(x) for x in b]
#     print(binary_search_index(c))
#
# Q3
# 考点：binary heap
# Top-K：实现容量为k的最小堆
# class min_heap:
#     def __init__(self,k):
#         self.a=[]
#         self.cap=k
#     def heapify_up(self,i):
#         while i>0:
#             parent=(i-1)//2
#             if self.a[parent]<self.a[i]:
#                 break
#             self.a[parent],self.a[i]=self.a[i],self.a[parent]
#             i=parent
#     def heapify_down(self,i):
#         n=len(self.a)
#         while True:
#             left=2*i+1
#             right=2*i+2
#             smallest=i
#             if left<n and self.a[smallest]>self.a[left]:
#                 smallest=left
#             if right<n and self.a[smallest]>self.a[right]:
#                 smallest=right
#             if smallest==i:
#                 break
#             self.a[smallest],self.a[i]=self.a[i],self.a[smallest]
#             i=smallest
#     def push_keep_topk(self,val):
#         if len(self.a)<self.cap:
#             self.a.append(val)
#             self.heapify_up(len(self.a)-1)
#         else:
#             if val>self.a[0]:
#                 self.a[0]=val
#                 self.heapify_down(0)
#     def top(self):
#         return self.a[0]
# def find_kth_largest(nums, k):
#     heap=min_heap(k)
#     for x in nums:
#         heap.push_keep_topk(x)
#     return heap.top()
# a=input().split()
# b=[int(x) for x in a]          
# num=input().split()
# nums=[int(x) for x in num]
# print(find_kth_largest(nums,b[1]))
#
# Q4
# leetcode 20 
# 考点：stack
# 嵌套配对用栈，撤销回退用栈，需要暂存中间态等条件满足再处理也用栈
# 901 → 921 → 1541 → 678 → 1249 → 2390
def isBal(s):
    match={')':'(',']':'[','}':'{'}
    stack=[]
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        else:
            if ch in ')]}':
                if not stack:
                    return False
                if match[ch]!=stack.pop():  # 在 if 判断里写 ls.pop()，确实已经出栈并修改了原列表
                    return False
    return not stack
#
# Q5 
# 考点：分治
# 我的版本
# def max_min(arr):
#     if len(arr)<=3:
#         return [min(arr),max(arr)]
#     cut1=len(arr)//3
#     cut2=cut1*2
#     a1=max_min(arr[:cut1])
#     a2=max_min(arr[cut1:cut2])
#     a3=max_min(arr[cut2:])
#     return merge(a1,a2,a3)
# def merge(a1,a2,a3):
#     re=[]
#     Max=max(a1[1],a2[1],a3[1])
#     Min=min(a1[0],a2[0],a3[0])
#     re.append(Min)
#     re.append(Max)
#     return re
# a=int(input())
# b=input().split()
# c=[int(x) for x in b]
# aws=max_min(c)
# print(aws[1]-aws[0])
#
# ChatGPT版本 -> 记三分模板(左闭右开)
def max_min_idx(arr, L=0, R=None):
    if R is None:
        R=len(arr)
    if R - L <= 3:  # 其实<=2也行
        return min(arr[L:R]), max(arr[L:R])
    
    # 三分模板！！！
    m1 = L + (R - L) // 3
    m2 = L + (2 * (R - L)) // 3

    mn1, mx1 = max_min_idx(arr, L, m1)
    mn2, mx2 = max_min_idx(arr, m1, m2)
    mn3, mx3 = max_min_idx(arr, m2, R)
    return (min(mn1, mn2, mn3), max(mx1, mx2, mx3))


# Exam B
# Q2
# strip("[]"): strip(chars) 会把chars里的所有字符当作“要删除的集合”，从左右两边不停删除，直到遇到不是这些字符的为止
# split(","):把字符串按 , 分割，返回一个列表
# def find_repe(arr):
#     l=0
#     r=len(arr)-1
#     while l<r:
#         mid=(l+r)//2
#         if arr[mid]==mid:
#             l=mid+1
#         else:
#             r=mid
#     return arr[l]
# # 注意的这里的输入形式是 [0,1,1,2,3] (带着[]和,)
# a=input().strip("[]").split(",")
# b=[int(x) for x in a]
# print(find_repe(b))
#
# Q3
class min_heap:
    def __init__(self,k):
        self.a=[]
        self.cap=k
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            if self.a[parent]<=self.a[i]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            smallest=i
            if left<n and self.a[smallest]>self.a[left]:
                smallest=left
            if right<n and self.a[smallest]>self.a[right]:
                smallest=right
            if smallest==i:
                break
            self.a[smallest],self.a[i]=self.a[i],self.a[smallest]
            i=smallest
    def push(self,pair):
        if len(self.a)<self.cap:
            self.a.append(pair)
            self.heapify_up(len(self.a)-1)
        else:
            if pair>self.a[0]:
                self.a[0]=pair
                self.heapify_down(0)
    def top(self):
        return -self.a[0][1]
# n=int(input())
# a=input().split()
# k=int(input())
# arr=[int(x) for x in a]
# fre={}
# for x in arr:
#     fre[x]=fre.get(x,0)+1
# heap=min_heap(k)
# for v,f in fre.items():
#     # 存-v是因为频率相同时需要的是值更小的留下来
#     heap.push((f,-v))
# print(heap.top())
"""
我的版本
class min_heap:
    def __init__(self,arr=None):
        self.a=[]
        if arr:
            self.a=list(arr)
            self.build_heap()
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            # 用元组整体比较: (-freq, val) -> 频率高在前, 同频val小在前
            if self.a[parent]<self.a[i]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            smallest=i
            # 也用元组整体比较
            if left<n and self.a[smallest]>self.a[left]:
                smallest=left
            if right<n and self.a[smallest]>self.a[right]:
                smallest=right
            if smallest==i:
                break
            self.a[smallest],self.a[i]=self.a[i],self.a[smallest]
            i=smallest
    def build_heap(self):
        n=len(self.a)
        for i in range((n-2)//2,-1,-1):
            self.heapify_down(i)
    def pop_min(self):
        self.a[0],self.a[-1]=self.a[-1],self.a[0]
        min_val=self.a.pop()
        self.heapify_down(0)
        return min_val
n=int(input())
a=input().split()
k=int(input())
arr=[int(x) for x in a]
# 统计频率用字典
fre={}
for x in arr:
    fre[x]=fre.get(x,0)+1
temp=[]
for v,f in fre.items():
    # 用 (-freq, value)：
    # 频率高 → -freq 更小 → 更靠前; 同频率 → value 小更靠前（满足“取更小元素”）
    # 若是最大堆，则是（f, -v）
    temp.append((-f,v))
heap=min_heap(temp)
for i in range(k):
    re=heap.pop_min()
print(re[1])
"""
#
# Q4
# leetcode 844 -> 字符串无缝拼接：''.join(listName)
def bs(s):
    stack=[]
    for ch in s:
        if ch=='#':
            if stack:
                stack.pop()
        else:
            stack.append(ch)
    return ''.join(stack)
#
# Q5 -> 恰好只剩一路才可以extend!
def tri_merge(a1,a2,a3,n1,n2,n3):
    i=j=k=0
    re=[]
    while i<n1 and j<n2 and k<n3:
        if min(a1[i],a2[j],a3[k])==a1[i]:
            re.append(a1[i])
            i+=1
        elif min(a1[i],a2[j],a3[k])==a2[j]:
            re.append(a2[j])
            j+=1
        else:
            re.append(a3[k])
            k+=1
    # 三路归并后要两路归并！不能直接extend！
    if i==n1:
        return merge(re,a2[j:],a3[k:])
    elif j==n2:
        return merge(re,a1[i:],a3[k:])
    else:
        return merge(re,a1[i:],a2[j:])
def merge(re,a,b):
    m=n=0
    while m<len(a) and n<len(b):
        if a[m]<=b[n]:
            re.append(a[m])
            m+=1
        else:
            re.append(b[n])
            n+=1
    re.extend(a[m:])
    re.extend(b[n:])
    return re
# l1=input().split()
# n=[int(x) for x in l1]
# l2=input().split()
# a1=[int(x) for x in l2]
# l3=input().split()
# a2=[int(x) for x in l3]
# l4=input().split()
# a3=[int(x) for x in l4]
# aws=tri_merge(a1,a2,a3,n[0],n[1],n[2])
# print(*aws)



# Exercise 06 Merge Two Linked List
"""
class ListNode:
    def __init__(self,val):
        self.val=val
        self.next=None
def build(n,arr):
    if n==0:
        return
    else:
        head=ListNode(arr[0])
        cur=head
        for i in range(1,n):
            cur.next=ListNode(arr[i])
            cur=cur.next
    return head
def merge_two_list(ls1,ls2):
    dummy=ListNode(-1)
    tail=dummy
    while ls1 and ls2:
        if ls1.val<=ls2.val:
            tail.next=ls1
            ls1=ls1.next
        else:
            tail.next=ls2
            ls2=ls2.next
        tail=tail.next
    tail.next=ls1 if ls1 else ls2
    return dummy.next

n=int(input())
a=input().split()
l1=[int(x) for x in a]
ls1=build(n,l1)
m=int(input())
b=input().split()
l2=[int(x) for x in b]
ls2=build(m,l2)
re=merge_two_list(ls1,ls2)
r=[]
while re:
    r.append(re.val)
    re=re.next
print(*r)
"""

# Exercise 08 3sum
"""
def three_sum(arr,n):
    arr.sort()
    re=[]
    for i in range(n-2):
        if i>0 and arr[i]==arr[i-1]:
            continue
        j=i+1
        k=n-1
        while j<k:
            s=arr[i]+arr[j]+arr[k]
            if s==0:
                re.append([arr[i],arr[j],arr[k]])
                j+=1
                k-=1
                while j<k and arr[j]==arr[j-1]:
                    j+=1
                while j<k and arr[k]==arr[k+1]:
                    k-=1
            elif s>0:
                k-=1
            else:
                j+=1
    return re
n=int(input())
a=input().split()
arr=[int(x) for x in a]
ans=three_sum(arr,n)
print(ans)
"""

# Exercise 09 Next Greater Element 1 
# 单调栈的应用！
"""
def nex_gre_ele(nums1,nums2):
    stack=[]
    re={}
    for x in reversed(nums2):
        while stack and stack[-1]<x:
            stack.pop()
        re[x]=stack[-1] if stack else -1
        stack.append(x)
    return [re[x] for x in nums1]
n1=int(input())
a=input().split()
nums1=[int(x) for x in a]
n2=int(input())
b=input().split()
nums2=[int(x) for x in b]
print(*nex_gre_ele(nums1,nums2))
"""

# Exercise 10 Next Greater Element 2 
"""
def nex_gre_ele2(nums,n):
    ans=[-1]*n
    stack=[]    # 因有重复，存下标
    for i in range(2*n-1,-1,-1):    # 扫两遍
        j=i%n   # 真正的下标
        while stack and nums[stack[-1]]<=nums[j]:
            stack.pop()
        if stack:
            ans[j]=nums[stack[-1]]
        stack.append(j)
    return ans
n=int(input())
a=input().split()
nums=[int(x) for x in a]
print(*nex_gre_ele2(nums,n))
"""

# Exercise 11 AVL Tree Insertion
"""
class Node:
    def __init__(self,val):
        self.val=val
        self.left=None
        self.right=None
        self.h=0    # 单节点高度为0
class avl_tree:
    def __init__(self,arr):
        self.root=None
        self.build(arr)
    def build(self,arr):
        self.root=None
        for x in arr:
            self.root=self.avl_insert(self.root,x)
    def avl_insert(self,t,x):
        if t is None:
            return Node(x)
        if x<t.val:
            t.left=self.avl_insert(t.left,x)
        else:
            t.right=self.avl_insert(t.right,x)
        return self.rebalance(t)
    def height(self,t):
        return t.h if t else -1
    def update(self,t):
        if t:
            t.h=1+max(self.height(t.left),self.height(t.right))
    def balance_factor(self,t):
        return self.height(t.left)-self.height(t.right) if t else 0
    def right_rotate(self,t):
        x=t.left
        B=x.right
        x.right=t
        t.left=B
        # 先低后高的顺序更新高度
        self.update(t)
        self.update(x)
        return x    
    def left_rotate(self,t):
        y=t.right
        B=y.left
        y.left=t
        t.right=B
        self.update(t)
        self.update(y)
        return y
    def rebalance(self,t):
        if not t:
            return None
        self.update(t)
        bf=self.balance_factor(t)
        if bf==2:   
            if self.balance_factor(t.left)<0:
                t.left=self.left_rotate(t.left)
            t=self.right_rotate(t)
        elif bf==-2:
            if self.balance_factor(t.right)>0:
                t.right=self.right_rotate(t.right)
            t=self.left_rotate(t)
        return t
    def pre_order(self,node,re):
        if node:
            re.append(node.val)
            self.pre_order(node.left,re)
            self.pre_order(node.right,re)
        return re
n=int(input())
a=input().split()
arr=[int(x) for x in a]
tree=avl_tree(arr)
ans=[]
ans=tree.pre_order(tree.root,ans)
print(*ans)
"""

# Exercise 12 rod cutting 
"""
def max_val(n,arr):
    best=[0]*(n+1)
    best[1]=arr[0]
    for i in range (2,n+1):
        best[i]=arr[i-1]
        for j in range(1,(i//2)+1): # 把(i//2)也包含
            best[i]=max(best[i],best[j]+best[i-j])
    return best[n]
n=int(input())
a=input().split()
arr=[int(x) for x in a]
print(max_val(n,arr))
"""

# Exercise 17 Backspace String Compare -- 不用stack
"""def compare(s1,s2):
    i,j=len(s1)-1,len(s2)-1
    skip1=skip2=0
    while i>=0 or j>=0:
        while i>=0:
            if s1[i]=='#':
                skip1+=1
                i-=1
            elif skip1>0:
                skip1-=1
                i-=1
            else:
                break
        while j>=0:
            if s2[j]=='#':
                skip2+=1
                j-=1
            elif skip2>0:
                skip2-=1
                j-=1
            else:
                break
        
        if i>=0 and j>=0:
            if s1[i]!=s2[j]:
                return False
        elif (i>=0 and j<0) or (j>=0 and i<0):
            return False
        i-=1
        j-=1
    return True
s1=input().strip()
s2=input().strip()
print("True" if compare(s1,s2) else "False")
"""

# Exercise 19 Maximum On-time Tasks 
"""
def merge_sort(tasks,l=0,r=None):
    if r is None:
        r=len(tasks)
    if r-l<=1:
        return tasks[l:r]
    mid=(l+r)//2
    left=merge_sort(tasks,l,mid)
    right=merge_sort(tasks,mid,r)
    return merge(left,right)
def merge(left,right):
    i=j=0
    re=[]
    while i<len(left) and j<len(right):
        if left[i][1]<=right[j][1]:
            re.append(left[i])
            i+=1
        else:
            re.append(right[j])
            j+=1
    re.extend(left[i:])
    re.extend(right[j:])
    return re

class maxheap:
    def __init__(self):
        self.a=[]
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            if self.a[parent][0]>self.a[i][0]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            biggest=i
            if left<n and self.a[biggest][0]<self.a[left][0]:
                biggest=left
            if right<n and self.a[biggest][0]<self.a[right][0]:
                biggest=right
            if biggest==i:
                break
            self.a[biggest],self.a[i]=self.a[i],self.a[biggest]
            i=biggest
    def insert(self,task):
        self.a.append(task)
        self.heapify_up(len(self.a)-1)
    def pop(self):
        self.a[0],self.a[-1]=self.a[-1],self.a[0]
        re=self.a.pop()
        self.heapify_down(0)
        return re
    def length(self):
        return len(self.a)
    
def schedule(tasks):
    total=0
    ddl=0
    new_tasks=merge_sort(tasks)
    heap=maxheap()
    for task in new_tasks:
        heap.insert(task)
        ddl=task[1]
        total+=task[0]
        if total>ddl:
            aban=heap.pop()
            total-=aban[0]
    return heap.length()

n=int(input())
tasks=[]
for _ in range(n):
    t,d=map(int,input().split())
    tasks.append((t,d))
print(schedule(tasks))        
"""

# Exercise 22 Jump Game 更优解法
"""
def jumpgame(nums):
    far = 0  # 当前能到达的最远下标
    n = len(nums)
    for i in range(n):
        if i > far:
            return False  # 连 i 都到不了，后面更不可能
        far = max(far, i + nums[i])
    return True
"""

# Exercise 24 回文数
"""
def palin(num):
    if num<0:
        return False
    if num==0:
        return True
    div=1
    temp=num
    while num>=10:
        num//=10
        div*=10
    while temp:
        l=temp//div
        r=temp%10
        if l!=r:
            return False
        temp=(temp%div)//10
        div//=100
    return True
n=int(input())
print("true") if palin(n) else print("false")
"""

# Exercise 30 Maximum Length of Repeated Subarray
"""
def max_repeated(n,m,nums1,nums2):
    dp=[[0]*(m+1) for _ in range(n+1)]
    maxi=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if nums1[i-1]==nums2[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
                maxi=max(maxi,dp[i][j]) # 注意这里
    return maxi
"""

# Exercise 26 Maximum Number of Events That Can Be Attended
"""
class minheap:
    def __init__(self):
        self.a=[]
    def heapify_up(self,i):
        while i>0:
            parent=(i-1)//2
            if self.a[parent][1]<self.a[i][1]:
                break
            self.a[parent],self.a[i]=self.a[i],self.a[parent]
            i=parent
    def heapify_down(self,i):
        n=len(self.a)
        while True:
            left=2*i+1
            right=2*i+2
            smallest=i
            if left<n and self.a[smallest][1]>self.a[left][1]:
                smallest=left
            if right<n and self.a[smallest][1]>self.a[right][1]:
                smallest=right
            if smallest==i:
                break
            self.a[smallest],self.a[i]=self.a[i],self.a[smallest]
            i=smallest
    def insert(self,event):
        self.a.append(event)
        self.heapify_up(len(self.a)-1)
    def pop(self):
        self.a[0],self.a[-1]=self.a[-1],self.a[0]
        re=self.a.pop()
        self.heapify_down(0)
        return re
    def length(self):
        return len(self.a)

def select(n,events):
    # 注意选择全局最大end
    max_end=max(e for _,e in events)
    heap=minheap()
    i=0
    ans=0
    for day in range(1,max_end+1):  # 从1开始
        while i<n and events[i][0]==day:
            heap.insert(events[i])
            i+=1
        while heap.length():
            if heap.pop()[1]>=day:
                ans+=1
                break
    return ans

n=int(input())
events=[]
for _ in range(n):
    s,e=map(int,input().split())
    events.append((s,e))
events.sort()
print(select(n,events))
"""

# Exercise 31 Jump Game 2
"""
def min_jumps(nums):
    n = len(nums)
    if n <= 1:
        return 0

    steps = 0       
    cur_end = 0      
    farthest = 0     

    for i in range(n - 1):  # 最后一个位置不需要再扩展
        farthest = max(farthest, i + nums[i])

        # 到了当前步的边界，需要“起跳”进入下一步
        if i == cur_end:
            steps += 1
            cur_end = farthest
            if cur_end >= n - 1:  # 已经能覆盖到最后一个位置了
                break

    return steps
"""

# Extra 01
def merge_sort_rep(arr,l=0,r=None):
    if r is None:
        r=len(arr)
    if r-l<=1:
        return arr[l:r], (1 if r-l==1 else 0)
    mid=(l+r)//2
    L,countl=merge_sort_rep(arr,l,mid)
    R,countr=merge_sort_rep(arr,mid,r)
    return merge_count(L,R)
def merge_count(L,R):
    i=j=0
    count=0
    re=[]
    while i<len(L) and j<len(R):
        if L[i]<=R[j]:  
            if not re or L[i]!=re[-1]:
                count+=1
            re.append(L[i])
            i+=1
        else:
            if not re or R[j]!=re[-1]:
                count+=1
            re.append(R[j])
            j+=1
    for a in L[i:]:
        if a!=re[-1]:
            count+=1
        re.append(a)
    for b in R[j:]:
        if b!=re[-1]:
            count+=1
        re.append(b)
    return re,count
# n=int(input())
# if n==0:
#     # print()
#     print(0)
# else:
#     b=input().split()
#     arr=[int(x) for x in b]
#     tz=merge_sort_rep(arr)
#     print(*tz[0])
#     print(tz[1])
# 或者正常归并排序然后：
def count_distinct_sorted(a):
    if not a: 
        return 0
    cnt = 1
    last = a[0]
    for x in a[1:]:
        if x != last:
            cnt += 1
            last = x
    return cnt

# Extra 02
def rev_qsort(arr,l=0,r=None):
    if r is None:
        r=len(arr)-1
    if l<r:
        pivot=partition(arr,l,r)
        rev_qsort(arr,l,pivot-1)
        rev_qsort(arr,pivot+1,r)
    return arr
def partition(arr,l,r):
    key=l
    i=l+1
    j=r
    while True:
        while i<=j and arr[i]>arr[key]:
            i+=1
        while j>=i and arr[j]<arr[key]:
            j-=1
        if j<i:
            break
        arr[i],arr[j]=arr[j],arr[i]
        i+=1
        j-=1
    arr[key],arr[j]=arr[j],arr[key]
    return j