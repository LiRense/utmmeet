class Solution:
    def addBinary(self, a: str, b: str) -> str:
        a = int(a, 2)
        b = int(b, 2)
        return bin(a+b)[2:]


sol = Solution()
print(sol.addBinary('11','1'))