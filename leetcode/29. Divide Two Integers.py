class Solution:
    def divide(self, dividend: int, divisor: int) -> int:
        flag = ''
        if dividend < 0 and divisor < 0:
            pass
        elif dividend < 0:
            flag = '-'
        elif divisor < 0:
            flag = '-'
        dividend = abs(dividend)
        divisor = abs(divisor)
        count = len(range(0,dividend-divisor+1,divisor))
        if flag == '-':
            count = -count
        count = min(max(count, -2**31),2**31-1)
        return count


sol = Solution()
print(sol.divide(-1,-1))