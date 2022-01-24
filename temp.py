from pickle import dump
with open("login.dat",'wb') as f:
    dump({"Anmol":"a",
          "Tanish":'t',
          "Uday":'u'},
         f)
    
