class Solution:
    def climbStairs(self, n: int) -> int:
            return self.requrvy(n)


    def requrvy(self,n):
        if n == 0:
            return 1
        if n < 0:
            return 0
        return self.requrvy(n-1) + self.requrvy(n-3)




sol = Solution()
# n - 1 + n - 2 + n - 3 + 1
print(sol.climbStairs(8))
