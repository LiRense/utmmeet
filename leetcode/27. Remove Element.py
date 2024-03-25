from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        if nums is None:
            return 0
        for i in range(nums.count(val)):
            nums.remove(val)
        return len(nums)


sol = Solution()

print(sol.removeElement([3,2,2,3],3))