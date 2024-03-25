from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        nums[:] = sorted(list(set(nums)))
        return len(nums)


nums = [1,1,2]
expectedNums = [1,2]

sol = Solution()

k = sol.removeDuplicates(nums)

assert k == len(expectedNums)
for i in range(k):
    assert nums[i] == expectedNums[i]