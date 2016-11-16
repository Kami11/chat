
class FunctionMapper:
    def __init__(self):
        self.all = {}
    def __call__(self, name):
        def decorator(func):
            self.all[name] = func
            return func
        return decorator

def is_ip(string):
    try:
        nums = [int(s) for s in string.split(".")]
    except ValueError:
        return False
    return len(nums) == 4 and all(0 <= n < 256 for n in nums)
