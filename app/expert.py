from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import itertools
import numpy as np
# Define la red bayesiana reducida
model = BayesianNetwork([
    ('Anxiety', 'PsychologicalIssue'),
    ('Depression', 'PsychologicalIssue'),
    ('Stress', 'PsychologicalIssue'),
    ('SleepProblems', 'PsychologicalIssue'),
])

# Define CPDs reducidos para cada síntoma
anxiety_values=[[0.7], [0.2],[0.1]]
dep_values=[[0.6], [0.3],[0.1]]
stress_values=[[0.5], [0.4],[0.1]]
sleep_values=[[0.65], [0.25],[0.1]]
cpd_anxiety = TabularCPD(variable='Anxiety', variable_card=3, values=anxiety_values)
cpd_depression = TabularCPD(variable='Depression', variable_card=3, values=dep_values)
cpd_stress = TabularCPD(variable='Stress', variable_card=3, values=stress_values)
cpd_sleep_problems = TabularCPD(variable='SleepProblems', variable_card=3, values=sleep_values)

evidence_combinations = list(itertools.product(range(3), repeat=4))

# Completa los valores del CPD de PsychologicalIssue
values_psychological_issue = []
for combination in itertools.product(range(3), repeat=4):
    values_for_combination = []
    for i in range(3):  # Iterar sobre los posibles valores de PsychologicalIssue
        # Calcular la probabilidad condicional para la combinación actual
        prob = (0.7 if combination[0] == i else 0.2) * (0.6 if combination[1] == i else 0.3) * (0.5 if combination[2] == i else 0.4) * (0.65 if combination[3] == i else 0.25)
        values_for_combination.append(prob)
    
    # Normalizar los valores para esta combinación
    total_prob = sum(values_for_combination)
    values_for_combination = [value / total_prob for value in values_for_combination]
    
    values_psychological_issue.append(values_for_combination)

# Transponer la matriz y convertirla de nuevo en una lista de listas
values_psychological_issue = np.array(values_psychological_issue).T.tolist()

# Define CPD reducido para la PsychologicalIssue
cpd_psychological_issue = TabularCPD(
    variable='PsychologicalIssue', variable_card=3,
    values=values_psychological_issue,
    evidence=['Anxiety', 'Depression', 'Stress', 'SleepProblems'],
    evidence_card=[3, 3, 3, 3]
)

# Agrega CPDs al modelo reducido
model.add_cpds(cpd_anxiety, cpd_depression, cpd_stress, cpd_sleep_problems, cpd_psychological_issue)

# Check model validity
assert model.check_model()

# Perform inference
inference = VariableElimination(model)

from experta import *



class PsychologicalAssessment(KnowledgeEngine):

    def get_responses(self):
        return self.responses

    def __init__(self, model):
        super().__init__()
        self.responses = []

    @Rule(Fact(sleep_quality=P(lambda x: x >= 1) & P(lambda x: x <= 3)))
    def high_sleep(self):
        self.responses.append("It's good that you are sleeping well. Keep up the good work! \n")

    @Rule(Fact(sleep_quality=P(lambda x: x == 3)))
    def almost_moderate_sleep(self):
        self.responses.append("Be careful though, your current sleep level is good but the score is close to the moderate level. \n")
        self.responses.append("As a recommendation, be careful and watch your sleep practices. \n")

    @Rule(Fact(sleep_quality=P(lambda x: x >= 4) & P(lambda x: x <= 6)))
    def moderate_sleep(self):
        self.responses.append("You have a moderate level of sleep. \n")
        self.responses.append("We recommend you not to neglect your sleep practices to avoid future problems. \n")
        self.responses.append("You will feel much better if you sleep well. Here are some practices and tips that you can implement: \n")
        self.responses.append("1. Implement a consistent schedule. \n")
        self.responses.append("2. Implement a relaxing bedtime routine. \n")
        self.responses.append("3. Eliminate distractions. Avoid using electronic devices before bed \n")
        self.responses.append("4. Use the bed only for sleeping. \n")
        self.responses.append("Seek professional help if the practices do not improve your sleep. \n")

    @Rule(Fact(sleep_quality=P(lambda x: x == 3)))
    def almost_low_sleep(self):
        self.responses.append("Pay attention to your sleep! \n Your current sleep level is moderate but the score is close to the low level. As a recommendation. \n")

    @Rule(Fact(sleep_quality=P(lambda x: x >= 7)))
    def low_sleep(self):
        self.responses.append("You have a low level of sleep. \n")
        self.responses.append("Lack of sleep can jeopardize your health in every way, especially emotionally. We strongly and respectfully recommend you seek professional help.")

    # ----------------- Depression -------------------------------

    @Rule(Fact(depression_level=P(lambda x: x >= 1) & P(lambda x: x <= 3)))
    def low_depression(self):
        self.responses.append("Your depression level is low. Keep up with your positive habits! \n")

    @Rule(Fact(depression_level=P(lambda x: x >= 4) & P(lambda x: x <= 6)))
    def moderate_depression(self):
        self.responses.append("You have a moderate level of depression. \n")
        self.responses.append("It's important to take steps to manage your depression to prevent it from worsening. \n")
        self.responses.append("Here are some suggestions: \n")
        self.responses.append("1. Engage in regular physical activity. \n")
        self.responses.append("2. Maintain social connections and talk to friends or family. \n")
        self.responses.append("3. Practice relaxation techniques like mindfulness or meditation. \n")
        self.responses.append("4. Consider speaking with a mental health professional. \n")

    @Rule(Fact(depression_level=P(lambda x: x >= 7)))
    def high_depression(self):
        self.responses.append("Your depression level is high. \n")
        self.responses.append("We strongly recommend you seek professional help immediately. \n")
        self.responses.append("Depression can significantly impact your quality of life, and professional support can make a huge difference. \n")

    @Rule(Fact(depression_level=P(lambda x: x == 3)))
    def almost_moderate_depression(self):
        self.responses.append("Be cautious, your depression level is getting close to moderate. \n")
        self.responses.append("It's important to monitor your mood and seek support if needed. \n")

    @Rule(Fact(depression_level=P(lambda x: x == 6)))
    def almost_high_depression(self):
        self.responses.append("Your depression level is getting close to high. \n")
        self.responses.append("We recommend reaching out to a mental health professional for assistance. \n")

    # ----------------- Stress -------------------------------

    @Rule(Fact(stress_level=P(lambda x: x >= 1) & P(lambda x: x <= 3)))
    def low_stress(self):
        self.responses.append("Your stress level is low. Keep up the good work in managing stress! \n")

    @Rule(Fact(stress_level=P(lambda x: x >= 4) & P(lambda x: x <= 6)))
    def moderate_stress(self):
        self.responses.append("You have a moderate level of stress. \n")
        self.responses.append("It's important to manage your stress to avoid potential health issues. \n")
        self.responses.append("Consider these tips: \n")
        self.responses.append("1. Practice deep breathing exercises. \n")
        self.responses.append("2. Take regular breaks and engage in leisure activities. \n")
        self.responses.append("3. Maintain a balanced diet and exercise routine. \n")
        self.responses.append("4. Reach out to a mental health professional if necessary. \n")

    @Rule(Fact(stress_level=P(lambda x: x >= 7)))
    def high_stress(self):
        self.responses.append("Your stress level is high. \n")
        self.responses.append("High stress can severely impact your health. \n")
        self.responses.append("We recommend seeking professional help to manage your stress effectively. \n")

    @Rule(Fact(stress_level=P(lambda x: x >= 2) & P(lambda x: x <= 4)))
    def almost_moderate_stress(self):
        self.responses.append("Your stress level is approaching moderate. \n")
        self.responses.append("Consider implementing stress management techniques to prevent escalation. \n")

    @Rule(Fact(stress_level=P(lambda x: x >= 6) & P(lambda x: x <= 8)))
    def almost_high_stress(self):
        self.responses.append("Your stress level is approaching high. \n")
        self.responses.append("It's essential to prioritize self-care and seek support from loved ones and professionals. \n")

    # ----------------- Anxiety -------------------------------

    @Rule(Fact(anxiety_level=P(lambda x: x >= 1) & P(lambda x: x <= 3)))
    def low_anxiety(self):
        self.responses.append("Your anxiety level is low. Continue with your effective coping strategies! \n")

    @Rule(Fact(anxiety_level=P(lambda x: x >= 4) & P(lambda x: x <= 6)))
    def moderate_anxiety(self):
        self.responses.append("You have a moderate level of anxiety. \n")
        self.responses.append("Managing anxiety is crucial to maintain your well-being. \n")
        self.responses.append("Here are some tips: \n")
        self.responses.append("1. Practice regular physical activity. \n")
        self.responses.append("2. Engage in relaxation techniques like yoga or meditation. \n")
        self.responses.append("3. Maintain a balanced diet and adequate sleep. \n")
        self.responses.append("4. Consider speaking with a mental health professional. \n")

    @Rule(Fact(anxiety_level=P(lambda x: x >= 7)))
    def high_anxiety(self):
        self.responses.append("Your anxiety level is high. \n")
        self.responses.append("High anxiety can significantly impact your daily life. \n")
        self.responses.append("We recommend seeking professional help to address your anxiety. \n")

    @Rule(Fact(anxiety_level=P(lambda x: x == 3)))
    def almost_moderate_anxiety(self):
        self.responses.append("Your anxiety level is getting close to moderate. \n")
        self.responses.append("Consider practicing relaxation techniques and seeking support if needed. \n")

    @Rule(Fact(anxiety_level=P(lambda x: x == 6)))
    def almost_high_anxiety(self):
        self.responses.append("Your anxiety level is getting close to high. \n")
        self.responses.append("It's important to prioritize self-care and seek professional help. \n")

    # ----------------- Psychological Issue Probability -------------------------------

    @Rule(Fact(psychological_issue_probability=P(lambda x: x > 0.0) & P(lambda x: x < 0.4)))
    def low_psychological_issue_probability(self):
        self.responses.append("Your probability of having a psychological issue is low. Keep up with your healthy lifestyle! \n")

    @Rule(Fact(psychological_issue_probability=P(lambda x: x > 0.3) & P(lambda x: x < 0.7)))
    def moderate_psychological_issue_probability(self):
        self.responses.append("You have a moderate probability of having a psychological issue. \n")
        self.responses.append("It's important to monitor your mental health and take preventive measures. \n")
        self.responses.append("We recommend that you seek support from mental health professionals and start attending therapy. It will be a great help! \n")

    @Rule(Fact(psychological_issue_probability=P(lambda x: x > 0.6)))
    def high_psychological_issue_probability(self):
        self.responses.append("Your probability of having a psychological issue is high. \n")
        self.responses.append("We strongly recommend seeking professional help to address potential psychological issues. \n")
        self.responses.append("Professional support can be vital in managing and improving your mental health. \n")
        self.responses.append("You are not alone, lean on those who can help you. \n")

def main():
  user_sleep_case = 0
  user_depression_case = 0
  user_stress_case = 0
  user_anxiety_case = 0
    
  print ("Welcome to the Mental health Expert System!")
  print ("Please provide us following information:.")
  user_sleep_quality_input = int(input ("From 1 to 10 how you rate your sleep quality (10 the best quality and 1 the worst quality): \n"))
  user_depression_level_input = int(input ("Do you have a feeling of depression? \n On a scale of 1 to 10, how strong is the feeling? (10 is the higher & 1 the lower): \n Select 1 if you don't feel any depression \n"))
  user_stress_level_input = int(input ("From 1 to 10 how stressed do you feel? (10 is the higher & 1 the lower): \n"))
  user_anxiety_level_input = int(input ("From 1 to 10 how anxious do you feel? (10 is the higher & 1 the lower): \n"))

  if user_sleep_quality_input > 6:
    user_sleep_case = 2
  elif user_sleep_quality_input > 3:
    user_sleep_case = 1
  else:
    user_sleep_case = 0

  if user_depression_level_input > 6:
    user_depression_case = 2
  elif user_depression_level_input > 3:
    user_depression_case = 1
  else:
    user_depression_case = 0

  if user_stress_level_input > 6:
    user_stress_case = 2
  elif user_stress_level_input > 3:
    user_stress_case = 1
  else:
    user_stress_case = 0

  if user_anxiety_level_input > 6:
    user_anxiety_case = 2
  elif user_anxiety_level_input > 3:
    user_anxiety_case = 1
  else:
    user_anxiety_case = 0

  evidence ={
      'Anxiety': user_anxiety_case,
      'Depression': user_depression_case, 
      'Stress': user_stress_case,  
      'SleepProblems': user_sleep_case,  
  }

  psychological_Issue_probability = inference.query(variables=['PsychologicalIssue'], evidence=evidence)

  expert = PsychologicalAssessment(model)
  expert.reset()
  expert.declare(Fact(sleep_quality=user_sleep_quality_input))
  expert.declare(Fact(depression_level=user_depression_level_input))
  expert.declare(Fact(stress_level=user_stress_level_input))
  expert.declare(Fact(anxiety_level=user_anxiety_level_input))
  expert.declare(Fact(psycological_issue_probability=psychological_Issue_probability))
  expert.run()

if __name__ == "__main__":
    main()