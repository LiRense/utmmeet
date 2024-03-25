from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        return self.requver(head)

    def requver(self,l):
        if l.next is None:
            return l
        if l is None:
            return l
        new = l.next
        if l.val == new.val:
            return ListNode(new.val, self.requver(new.next))
        else:
            return ListNode(l.val,self.requver(l.next))





sol = Solution()
print(sol.deleteDuplicates(ListNode(1,ListNode(2,ListNode(2)))))