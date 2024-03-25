class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        words = s.split(' ')
        count = words.count('')
        for i in range(count):
            words.remove('')
        return len(words[len(words)-1])

sol =Solution()
print(sol.lengthOfLastWord('   fly me   to   the moon  '))