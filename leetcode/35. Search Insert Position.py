from typing import List


class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        if target in nums:
            return nums.index(target)
        else:
            nums.append(target)
            nums = sorted(nums)
            return nums.index(target)


sol = Solution()
print(sol.searchInsert([1,3,5,6,5],5))