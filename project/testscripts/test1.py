# #
# #
# # class Test():
# #
# #     def __init__(self):
# #
# #         self.common = 'Hello'
# #         print(self.common)
# #
# #     def print1(self):
# #         print(self.common + ' print1')
# #
# #
# #     def print2(self):
# #         print(self.common + ' print2')
#
#
# from service.qry import Cursor
#
#
# a = Cursor()
#
# for i in range(10):
#     a.querycommit("""
#       UPDATE dbo.TestTable
#       SET FUNC_KEY = '""" + str(i) + """'
#       WHERE ENGP_ENGNRG_PART_R = '4H231A188AA'""")
#
#
#     print(Cursor().queryresult('SELECT * FROM dbo.TestTable'))
#
