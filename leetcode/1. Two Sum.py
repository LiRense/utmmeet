from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        nums_list = []
        new_target = target
        for id, value in enumerate(nums):
            new_target -= value
            for id2, value2 in enumerate(nums[id+1::]):
                if new_target == value2:
                    return [id,id2+id+1]
            new_target = target







solution = Solution()
print(solution.twoSum([3,2,4],6))