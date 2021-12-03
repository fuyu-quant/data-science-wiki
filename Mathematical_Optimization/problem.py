#problem.py
import pandas as pd
import pulp

class CarGroupProblem():
  def __init__(self, students_df, cars_df, name='ClubCarProblem'):
    #初期化メソッド
    self.students_df = students_df
    self.cars_df = cars_df
    self.name = name
    self.prob = self._formulate()
    
  def _formulate(self):
    prob = pulp.LpProblem('ClubCarProblem',pulp.LpMinimize)
    S = self.students_df['student_id'].to_list()
    C = self.cars_df['car_id'].to_list()
    G = [1,2,3,4]
    #学生と車のペアのリスト
    SC = [(s,c) for s in S for c in C]
    #免許を持っている学生のリスト
    S_license = self.students_df[self.students_df['license'] == 1]['student_id']
    #学年がgの学生のリスト
    S_g = {g: self.students_df[self.students_df['grade'] == g]['student_id'] for g in G}
    #男性と女性のリスト
    S_male = self.students_df[self.students_df['gender'] == 0]['student_id']
    S_female = self.students_df[self.students_df['gender'] == 1]['student_id']
    #車の乗車定員の定数
    U = self.cars_df['capacity'].to_list()
    
    #変数
    #学生をどの車に割り当てるかを変数として定義
    x = pulp.LpVariable.dicts('x', SC, cat = 'Binary')
    
    #制約
    #各学生を一つの車に割り当てる
    for s in S:
      prob += pulp.lpSum([x[s,c] for c in C]) == 1
      
    #各車は乗車定員以下の人しか乗せられない
    for c in C:
      prob += pulp.lpSum([x[s,c] for s in S]) <= U[c]
    #免許証を持っている人の条件
    for c in C:
      prob += pulp.lpSum([x[s,c] for s in S_license]) >= 1
    
    #懇親を目的とした制約
    for c in C:
      for g in G:
        prob += pulp.lpSum([x[s,c] for s in S_g[g]]) >= 1
        
    #男を一人以上割り当てる
    for c in C:
      prob += pulp.lpSum([x[s,c] for s in S_male]) >= 1
    
    #女を一人以上割り当てる
    for c in C:
      prob += pulp.lpSum([x[s,c] for s in S_female]) >= 1
      
    #最適化後に利用するデータを返却
    return{'prob': prob,'variable' : {'x':x},'list':{'s':s,'c':c}}
           
  def solve(self):
      #最適化問題を解くメソッド
      status = self.prob['prob'].solve()
      
      #最適化結果の格納
      x = self.prob['variable']['x']
      S = self.prob['list']['S']
      C = self.prob['list']['C']
      Car2students = {c: [s for s in S if x[s,c].value() == 1] for c in C}
      solution_df = pd.DataFrame(list(student2car.item()),clumns=['student_id','car_id'])
      return solution_df
    
if __name__ == '__main__':
  #データの読み込み
  students_df = pd.read_csv('resource/students.csv')
  cars_df = pd.read_csv('resource/car.csv')
  
  prob = CarGroupProblem(students_df,cars_df)
  
  solution_df = prob.solve()
  
  print('Solution: \n',solution_df)
                                 
                                 
           



    
