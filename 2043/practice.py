# 在 Python 里，list + list 是 拼接（concatenation）操作

# python 'dict'
# dict={}  dict["Kobe"]=  按键查找
# if "Kobe" in dict:

# 类继承
# class sonClass(DadClass):
#   如何用到父类构造函数 -> super()
#   比如说父类有 name 和 age
#     def __init__(self, name, age):
#         super().__init__(name, age)
#         self.sex = Kobe
#
# Example
class HR:
    def __init__(self,name,id):
        self.name=name
        self.id=id
    def print_info(self,name,id):
        print(name)
        print(id)
class FT(HR):
    def __init__(self,name,id,monthly_salary):
        super().__init__(name,id)
        self.monthly_salary=monthly_salary
    def calculate_monthly_pay(self):
        return self.monthly_salary
class PT(HR):
    def __init__(self,name,id,daily_salary,workdays):
        super().__init__(name,id)
        self.daily_salary=daily_salary
        self.workdays=workdays
    def calculate_monthly_pay(self):
        return self.daily_salary * self.workdays


# 二分查找系列问题
def binary_search(A, x):
    left, right = 0, len(A) - 1
    while left <= right:
        mid = (left + right) // 2
        if A[mid] == x:
            return mid
        elif A[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
    return -1   # not found

# P34 ！！！！！！！
def lower_bound(a, x):
    l, r = 0, len(a)
    while l < r:
        m = (l + r) // 2
        if a[m] < x:
            l = m + 1
        else:
            r = m
    return l
def upper_bound(a, x):
    l, r = 0, len(a)
    while l < r:
        m = (l + r) // 2
        if a[m] <= x:
            l = m + 1
        else:
            r = m
    return l
def searchRange(nums, target):
    L = lower_bound(nums, target)
    if L == len(nums) or nums[L] != target:
        return [-1, -1]
    R = upper_bound(nums, target)-1
    return [L, R]
# 或者
def searchRange(nums, target):
    def lower_bound(nums, x):
        l, r = 0, len(nums)
        while l < r:
            mid = (l + r) // 2
            if nums[mid] >= x:
                r = mid
            else:
                l = mid + 1
        return l
    
    left = lower_bound(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]

    right = lower_bound(nums, target+1) - 1
    return [left, right]

# P74
# total_row=len(matrix)-1
# total_col=len(matrix[row_index])-1
# 把矩阵视作一维，再把下标k映射回二维：
# row=k // total_col
# col=k % total_col
# 因为k=row * total_col + col

# P162 爬坡二分查找
def findPeakElement(nums):
    left=0
    right=len(nums)-1
    while left<right:
        mid=(left+right)//2
        if nums[mid]<nums[mid+1]:
            left=mid+1
        else:
            right=mid
    return left

# P540 判断奇偶思路
# 在唯一数之前，每”对儿“的第一个元素落在偶数下标
# 在唯一数之后，每“对儿”的第一个元素落在奇数下标
def singleNonDuplicate(nums):
    l,r=0,len(nums)-1
    while l<r:
        mid=(l+r)//2
        if mid%2==1:
            mid-=1  # 强制mid为偶数，方便检查(mid,mid+1)
        if nums[mid]==nums[mid+1]:
            l=mid+2
        else:
            r=mid
    return nums[l]

# P33
def search_in_rotated(nums,target):
    left=0
    right=len(nums)-1
    while left<=right:
        mid=(left+right)//2
        if nums[mid]==target:
            return mid
        if nums[left]<=nums[mid]:   # =是为了考虑左有序数列仅仅一个元素
            if nums[left]<=target<nums[mid]:
                right=mid-1
            else:
                left=mid+1
        else:
            if nums[mid]<target<=nums[right]:
                left=mid+1
            else:
                right=mid-1
    return -1

# P1011：想清楚什么情况下能二分什么情况不能
def shipWithinDays(weights, days):
        lo=max(weights) # 最小也不能比单件的最大值小
        hi=sum(weights) # 最大是一次性全拿完
        # 二分查找最小可行值模板：
        # while lo<hi + 可行→hi=mid / 不可行→lo=mid+1 + 返回 lo
        while lo<hi:    
            mid=(lo+hi)//2
            if possible(weights,days,mid)==True:
                hi=mid  # 防止mid可行时把mid排除
            else:
                lo=mid+1
        return lo
def possible(weights,days,capacity):
    # 想清楚这里不能用二分查找
    used_days=1 # ！！从1开始是因为capacity足够大的时候只需一天，但循环里不溢出就不+1
    cur=0
    for w in weights:   
        if w>capacity:  # 及时跳出
            return False
        if cur+w<=capacity: # 不溢出不切
            cur+=w
        else:
            used_days+=1    # 溢出才切一刀
            cur=w   # 新的bucket
    return used_days<=days  # <=是为了二分查找
    
# 洛谷 P1873
def min_height(arr,m):
    left=0
    right=max(arr)
    ans=-1
    while left<=right:  # 加=
        mid=(left+right)//2
        total=0
        for t in arr:
            if t>mid:
                total+=(t-mid)
        if total>=m:  # 至少为m米
            ans=mid
            left=mid+1
        else:
            right=mid-1
    return ans


# 排序
def bubble_sort(arr):
    for i in range (len(arr)-1):
        swap=False
        for j in range (len(arr)-i-1):
            if arr[j]>arr[j+1]:
                arr[j],arr[j+1]=arr[j+1],arr[j]
                swap=True
        if swap==False:
            break
    return arr

def selection_sort(arr):
    for i in range (len(arr)-1):
        min_index=i
        for j in range (i+1,len(arr)):
            if arr[j]<arr[min_index]:
                min_index=j
        arr[i],arr[min_index]=arr[min_index],arr[i]
    return arr

def insertion_sort(arr):
    for i in range (1,len(arr)):  
        key=arr[i]
        j=i-1
        while j>=0 and arr[j]>key:  # 第一个是>=,为了包括第一个元素; 第二个是>,为了排序稳定
            arr[j+1]=arr[j]
            j-=1
        arr[j+1]=key
    return arr

def counting_sort(arr):
    if not arr:
        return []
    U=max(arr)+1  
    A=[0]*U
    re=[]
    for i in range (len(arr)):
        A[arr[i]]+=1
    for i in range (U):
        while A[i]>0:
            re.append(i)
            A[i]-=1
    return re

def merge_sort(arr,L=0,R=None): 
    # L=0, R=None 是初始化默认参数
    # 递归时传入的新 L, R 会覆盖默认参数
    # 所以可以直接叫merge_sort(A)
    if R is None:
        R=len(arr)  # [a:b]是左闭右开区间
    if R-L<=1:  # base case: 没有或只有一个元素
        return arr[L:R]
    mid=(L+R)//2
    l=merge_sort(arr,L,mid)
    r=merge_sort(arr,mid,R)
    return merge(l,r)
def merge(l,r):
    re=[]
    i=j=0   
    while i<len(l) and j<len(r):
        if l[i]<=r[j]:  
            re.append(l[i])
            i+=1
        else:
            re.append(r[j])
            j+=1
    re.extend(l[i:])    # 只添加剩余元素，故[i:]
    re.extend(r[j:])    
    return re

def quick_sort(arr,l=0,r=None):
    if r is None:
        r=len(arr)-1
    if l<r: # 注意是if
        pivot=partition(arr,l,r)
        quick_sort(arr,l,pivot-1)
        quick_sort(arr,pivot+1,r)
    return arr
def partition(arr,l,r):
    pivot=arr[l]
    left=l+1
    right=r
    while True:
        while left<=right and arr[left]<pivot:
            left+=1
        while left<=right and arr[right]>pivot:
            right-=1
        if left>right:
            break
        arr[left],arr[right]=arr[right],arr[left]
        left+=1
        right-=1
    arr[l],arr[right]=arr[right],arr[l]
    return right

# P912 -> 注意pivot随机选取
# class Solution:
#     def sortArray(self, nums: List[int]) -> List[int]:
#         self.quick_sort(nums,0,len(nums)-1)
#         return nums
#     def quick_sort(self,nums,l,r):
#         if l<r:
#             pivot=self.partition(nums,l,r)
#             self.quick_sort(nums,l,pivot-1)
#             self.quick_sort(nums,pivot+1,r)
#     def partition(self,nums,l,r):
#         # 随机选一个pivot
#         rand_index=random.randint(l,r)
#         nums[l],nums[rand_index]=nums[rand_index],nums[l]
#         key=l
#         left=l+1
#         right=r
#         while True:
#             while left<=right and nums[left]<nums[key]:
#                 left+=1
#             while right>=left and nums[right]>nums[key]:
#                 right-=1
#             if left>right:
#                 break
#             nums[left],nums[right]=nums[right],nums[left]
#             left+=1
#             right-=1
#         nums[right],nums[key]=nums[key],nums[right]
#         return right

# P88
class Solution:
    def merge(self, nums1, m, nums2, n):
        # 从尾部插入
        p1,p2,p=m-1,n-1,m+n-1
        while p2>=0:    # 关键：只要nums2还有没放进去的，就继续
            if p1>=0 and nums1[p1]>nums2[p2]:
                nums1[p]=nums1[p1]
                p1-=1
            else:
                nums1[p]=nums2[p2]
                p2-=1
            p-=1

# P21
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeTwoLists(self, list1, list2):
        # list1和list2是两个指针，指向链表的头节点（题干）
        # 建一个哑节点dummy，可省略链表没头的麻烦分支
        dummy=ListNode(-1)
        tail=dummy
        while list1 and list2: # while list1 = while list1 is not None
            if list1.val<-list2.val:
                tail.next=list1
                list1=list1.next
            else:
                tail.next=list2
                list2=list2.next
            tail=tail.next  # tail始终指向最后一个节点
        tail.next=list1 if list1 else list2
        return dummy.next   # 真正的头节点
        

# paper exercises
# Exercise 1
# P5
# 第j天最优利润：A[j] - min{A[1],A[2],…,A[j-1]}
def max_profit(arr):
    min_price=arr[0]
    max_profit=-1
    for price in arr[1:]:
        profit=price-min_price
        max_profit=max(profit,max_profit)
        min_price=min(price,min_price)
    return max_profit

# Exercise 2
# P1-Q1.2
def iterative_merge_sort(arr):
    n=len(arr)
    curr_size=1 # size of subarrays to merge
    while curr_size<n:
        left=0
        while left<n-1:
            mid=min(left+curr_size-1,n-1)
            right=min(left+2*curr_size-1,n-1)
            if mid<right:
                merge(arr,left,mid,right)
            # next two subarray to merge
            left+=2+curr_size
        curr_size*=2
        
# P5 数逆序对
"""
逆序对计数可以嵌入归并排序过程：
	1.	分治： 分别算左右部分的逆序对数并排好序。
        return 合并后数组, 左逆序 + 右逆序 + 跨逆序
	2.	归并： 在合并两个有序数组时，统计“跨越左右两边”的逆序对数。
        idea:此阶段左右两部分不需要维持原数组中顺序，因为任意左边元素都在右边前
	    举例：当左边的数大于右边的某个数时，因为左边数组有序，所以左边“剩下的所有数”都会比右边这个数大。
"""
def sort_and_count(arr):
    if len(arr)<=1:
        return arr,0
    mid=len(arr)//2
    L,l_count=sort_and_count(arr[:mid])
    # 这么写是因为sort_and_count返回的是一个二元tuple
    R,r_count=sort_and_count(arr[mid:])
    merged,cross_count=merge_and_count(L,R)
    return merged,l_count+r_count+cross_count
def merge_and_count(L,R):
    i=j=0
    merged=[]
    cross_count=0
    # 对于右边每个元素，统计左边有几个比它大的
    while i<len(L) and j<len(R):
        if L[i]<=R[j]:
            merged.append(L[i])
            i+=1
        else:
            cross_count+=(len(L)-i) # len(L)个元素减去0--(i-1)共i个元素
            merged.append(R[j])
            j+=1
    merged.extend(L[i:])
    merged.extend(R[j:])
    return merged,cross_count    

# leetcode 53
def max_sub(arr,l=0,r=None):
    if r is None:
        r=len(arr)
    if r-l==1:
        val=arr[l]
        return val,val,val,val
    mid=(l+r)//2
    lsum,lmax,llhs_max,lrhs_max=max_sub(arr,l,mid)
    rsum,rmax,rlhs_max,rrhs_max=max_sub(arr,mid,r)
    return merged_max(lsum,lmax,llhs_max,lrhs_max,rsum,rmax,rlhs_max,rrhs_max)
def merged_max(lsum,lmax,llhs_max,lrhs_max,rsum,rmax,rlhs_max,rrhs_max):
    new_max=max(lmax,rmax,lrhs_max+rlhs_max)
    new_lhs_max=max(llhs_max,lsum+rlhs_max)
    new_rhs_max=max(rrhs_max,rsum+lrhs_max)
    return lsum+rsum,new_max,new_lhs_max,new_rhs_max

"""
动态规划
def fib(n):
    if n<=1:
        return n
    prev1,prev2=0,1
    for i in range(2,n+1):
        cur=prev1+prev2
        prev1,prev2=prev2,cur
    return prev2

def knapsack(weights, values, W):
    n = len(weights)
    dp = [[0]*(W+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for w in range(1, W+1):
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i-1][w],
                               dp[i-1][w-weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][W]

def minCoins(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # base case
    for x in range(1, amount + 1):
        for coin in coins:
            if coin <= x:
                dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

def max_subarray(nums):
    dp = ans = nums[0]
    for x in nums[1:]:
        dp = max(x, dp + x)  
        ans = max(ans, dp)  
    return ans
"""

# Jump Game贪心
"""
def jumpgame(n,nums):
    dp=[False]*n
    dp[0]=True
    for i in range(n):
        if dp[i]:
            for j in range(nums[i]+1):
                if i+j<n:
                    dp[i+j]=True
    return dp[len(nums)-1]
n=int(input())
a=input().split()
nums=[int(x) for x in a]
print("true") if jumpgame(n,nums) else print("false")

def jumpgame2(n,nums):
    dp=[False]*n
    dp[0]=True
    step=[0]*n
    for i in range(n):
        if dp[i]:
            for j in range(1,nums[i]+1):
                if i+j<n:
                    dp[i+j]=True
                    if step[i+j]==0:
                        step[i+j]=step[i]+1
                    else:
                        step[i+j]=min(step[i]+1,step[i+j])
    return step[-1]
n=int(input())
a=input().split()
nums=[int(x) for x in a]
print(jumpgame2(n,nums))
"""
