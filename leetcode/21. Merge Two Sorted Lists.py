from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        if list1 is None:
            return list2
        elif list2 is None:
            return list1
        elif list1 is None and list2 is None:
            return None

        lis3 = []
        while list1 is not None or list2 is not None:
            if list1 != None:
                lis3.append(list1.val)
                list1 = list1.next
            if list2 != None:
                lis3.append(list2.val)
                list2 = list2.next
        lis3 = sorted(lis3)
        rec = self.recursivy(lis3)
        return rec

    def recursivy(self, lis3):
        if len(lis3) > 1:
            return ListNode(lis3[0], self.recursivy(lis3[1:]))
        elif len(lis3) == 1:
            return ListNode(lis3[0])






solut = Solution()

# print(solut.mergeTwoLists((ListNode(1,
#                                    ListNode(2,
#                                             ListNode(3,
#                                                      ListNode(4,None))))),
#                            ListNode(4,None)))

print(solut.mergeTwoLists(ListNode(),
                           ListNode()
                          ))