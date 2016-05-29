# coding: utf-8

"""
    kmp算法
    ```````

    实现搜索排序(字符粒度)
"""


def make_next(t, next):
    j = 0
    n = len(t)
    next.append(0)
    for i in range(1, n):
        while(j > 0 and (t[j] != t[i])):
            j = next[j-1]
        if (t[i] == t[j]):
            j = j+1
        next.append(j)

def kmp(s, t):
    """
    s: target string
    t: pattern string
    """
    j = 0
    m = len(s); n = len(t)
    next = []
    make_next(t, next)
    for i in range(m-n+1):
        while (s[i] == t[j]):
            i += 1
            j += 1
            if (j == n - 1):
                return (i-j+1)
            if (j == n):
                break
        else:
            j = next[j]
    return False
