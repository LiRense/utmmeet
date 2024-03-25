class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        for i in range(len(haystack)):
            if haystack[i] == needle[0]:
                if len(haystack[i:]) < len(needle):
                    break
                counter = 1
                for j in range(1,len(needle)):
                    if haystack[i+j] == needle[j]:
                        counter +=1
                if counter == len(needle):
                    return i
        return -1


sol = Solution()
print(sol.strStr('aaa','aaaa'))