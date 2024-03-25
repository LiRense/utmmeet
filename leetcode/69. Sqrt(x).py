class Solution:
    def mySqrt(self, x: int) -> int:

        return self.reqursive(0,x,x)

    def reqursive(self,start,end,x):
        middle = round((start + end) / 2)
        start = round(start)
        end = round(end)
        if end-start <= 1:
            if end*end > x:
                return start
            return end
        elif middle * middle > x:
            return self.reqursive(start,middle,x)
        elif middle*middle < x:
            return self.reqursive(middle, end,x)
        else:
            return round(middle)


sol = Solution()
print(sol.mySqrt(4))