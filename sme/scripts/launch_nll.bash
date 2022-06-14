
combine -M GenerateOnly ./inputs/m_dilep_cLXX_workspace_2016.root  -t -1 --saveToys --setParameters cLXX=0
combineTool.py -M FastScan -w ./inputs/m_dilep_cLXX_workspace_2016.root:w -d higgsCombineTest.GenerateOnly.mH120.123456.root:toys/toy_asimov
