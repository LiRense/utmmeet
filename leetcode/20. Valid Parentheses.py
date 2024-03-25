class Solution(object):
    def isValid(self, s):
        dic = {'(': ')', '[': ']', '{': '}'}
        stack = []

        for i in s:
            if i in '([{':
                stack.append(i)
            elif len(stack) == 0 or i != dic[stack.pop()]:
                return False
        if len(stack) > 1:
            return True
        else:
            return False


solut = Solution()

print(solut.isValid('[]'))


