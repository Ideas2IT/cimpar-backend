# a = (1,2,4)
# b = [1,2,4]
#
# b.append(3)
# print(b)
# a.append(3)

#
# c = {
#     "device_id": ["1", "2", "3"],
#     "mfg_id": ["2", "4", "6"],
#     "mfg_year": [1992, None, 1993],
#     "mfg_name": ["a", "b", "c"]
# }
#
# for key, val in c.items():
#     count = 0
#     for each_ele in val:
#         if not each_ele:
#             count += 1
#     print(f"{key} has {count} None values")


# a = [1, 3, 5, 7]
# k = 8
# # print(a[::-1])
# for

# a = "12121"
# c = a.split()
# print(c)
# b = "".join(c)
#
# print(a==b)
# b = []
# for each_ele in a.split()[::-1]:
#     b.append(each_ele)

# a = [1,2,3,4,5]
#
# b = [5,6,7,8,9]
#
# count1 = 0
# count2 = 0
#
# while True:
#     if a[count1] == b[count2]:
#         print(f"Matched {a[count1]}")
#         break
#     count1 += 1 if count1 < len(a) else 0
#     if a[count1-1] == a[-1]:
#         count2 += 1 if count2 < len(b) else 0
#         count1 = 0
#     if a[count1-1] == a[-1] and b[count2-1] == b[-1]:
#         print("No matching record")
#         break
