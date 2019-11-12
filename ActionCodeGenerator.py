#!/usr/bin/env python

import sys
import getopt
from pathlib import Path


#TODO  what happens of no name of the package is given e.g. GripperCommand


class UROSActionCodeGenerator:

    def __init__(self, ActionDefinitionFile):
        try:
            opts, args = getopt.getopt(ActionDefinitionFile, "hi:", ["ifile="])
        except getopt.GetoptError:
            sys.exit(2)

        self.Path = ''

        if len(args) > 1:
            self.Path = args[1]
        else:
            print("not path provided")
            sys.exit(2)

        self.Path = Path('.') / self.Path

        self.PackageName = self.Path.absolute().parts[-3]
        self.FileName = self.Path.parts[-1]
        self.ActionName = self.PackageName + '/' + self.Path.stem

        if not self.Path.exists():
            print('File not found.')
            sys.exit(3)

        Goal = []
        Feedback = []
        Result = []

        with self.Path.open() as ActionFile:
            ActionDefinition = ActionFile.readlines()
            FileParser = UROSActionDefinitionParser(ActionDefinition)
            Goal, Feedback, Result = FileParser.GetGoalFeedbackResult()

        PathForGeneratedFiles = self.Path.parent / ".." / "msg"

        AGCG = UROSActionGoalCodeGenerator(self.Path)
        AGCG.MySaveFile(PathForGeneratedFiles)

        GCG = UROSGoalCodeGenerator(self.Path, Goal)
        GCG.MySaveFile(PathForGeneratedFiles)

        ARCG = UROSActionResultCodeGenerator(self.Path)
        ARCG.MySaveFile(PathForGeneratedFiles)

        RCG = UROSResultCodeGenerator(self.Path, Result)
        RCG.MySaveFile(PathForGeneratedFiles)

        AFCG = UROSActionFeedbackCodeGenerator(self.Path)
        AFCG.MySaveFile(PathForGeneratedFiles)

        FCG = UROSFeedbackCodeGenerator(self.Path, Feedback)
        FCG.MySaveFile(PathForGeneratedFiles)


class UROSActionDefinitionParser:

    def __init__(self, ActionDefinition):
        self.ActionDefinition = ActionDefinition
        self.Goal = []
        self.Feedback = []
        self.Result = []

        self.RemoveCommentsAndEmptyLines()
        self.FillGoalResultFeedback()

    def RemoveCommentsAndEmptyLines(self):
        CleanedDefinition = []
        for line in self.ActionDefinition:
            SplitLine = line.split('#', 1)[0]
            # if not line[0] == '#':
            print("test")
            print(SplitLine)
            if not SplitLine == '':
                if not SplitLine == '\n':
                    if(SplitLine.endswith('\n')):
                        CleanedDefinition.append(SplitLine[:-1])
                    else:
                        CleanedDefinition.append(SplitLine)
        self.ActionDefinition = CleanedDefinition

    def FillGoalResultFeedback(self):
        section = 0
        for line in self.ActionDefinition:
            if not line == '---':
                if not line.find("Header") == -1:
                    line = "std_msgs/Header header"
                if section == 0:
                    self.Goal.append(line)
                elif section == 1:
                    self.Result.append(line)
                elif section == 2:
                    self.Feedback.append(line)
                else:
                    print('Invalid file format for Action Definition')
                    sys.exit(4)
            else:
                section += 1

    def GetGoal(self):
        return self.Goal

    def GetResult(self):
        return self.Result

    def GetFeedback(self):
        return self.Feedback

    def GetGoalFeedbackResult(self):
        return [self.GetGoal(), self.GetFeedback(), self.GetResult()]


class UCodeGenerator:

    def __init__(self, InPath):
        self.Path = Path('.') / InPath
        self.PackageName = self.Path.absolute().parts[-3]
        # self.FileName= self.Path.parts[-1]
        self.FileNameStem = self.Path.stem
        self.NameOption = ""
        self.ActionName = self.PackageName + '/' + self.Path.stem
        self.Data = []

    def FillData(self, DataDefinition):
        for Element in DataDefinition:
            self.Data.append(Element + "\n")
        print(self.Data)

    def MySaveFile(self, FolderPath):
        self.OutputPath = FolderPath / (self.FileNameStem + self.NameOption + ".msg")
        with self.OutputPath.open('w') as File:
            File.writelines(self.Data)


class UROSActionGoalCodeGenerator(UCodeGenerator):

    def __init__(self, InPath):
        super().__init__(InPath)

        self.NameOption = "ActionGoal"
        self.Data.append("std_msgs/Header header\n")
        self.Data.append("actionlib_msgs/GoalID goal_id\n")
        self.Data.append(self.ActionName + "Goal" + " goal\n")


class UROSGoalCodeGenerator(UCodeGenerator):

    def __init__(self, InPath, GoalDefinition):
        super().__init__(InPath)

        self.GoalDefinition = GoalDefinition
        self.NameOption = "Goal"
        self.FillData(self.GoalDefinition)


class UROSActionFeedbackCodeGenerator(UCodeGenerator):

    def __init__(self, InPath):
        super().__init__(InPath)

        self.NameOption = "ActionFeedback"
        self.Data.append("std_msgs/Header header\n")
        self.Data.append("actionlib_msgs/GoalStatus status\n")
        self.Data.append(self.ActionName + "Feedback" + " feedback\n")
        print(self.Data)

        # OutputPath = FolderPath / self.ActionName.parts[-1] +  ".msg"
        # print(OutputPath)
        # with Path.open()


class UROSFeedbackCodeGenerator(UCodeGenerator):

    def __init__(self, InPath, FeedbackDefinition):
        super().__init__(InPath)
        self.NameOption = "Feedback"
        self.FeedbackDefinition = FeedbackDefinition
        self.FillData(self.FeedbackDefinition)


class UROSActionResultCodeGenerator(UCodeGenerator):

    def __init__(self, InPath):
        super().__init__(InPath)
        self.NameOption = "ActionResult"
        self.Data.append("std_msgs/Header header\n")
        self.Data.append("actionlib_msgs/GoalStatus status\n")
        self.Data.append(self.ActionName + "Result" + " result\n")
        print(self.Data)


class UROSResultCodeGenerator(UCodeGenerator):

    def __init__(self, InPath, ResultDefinition):
        super().__init__(InPath)

        self.NameOption = "Result"
        self.ResultDefinition = ResultDefinition
        self.FillData(self.ResultDefinition)


if __name__ == '__main__':
    UROSActionCodeGenerator(sys.argv)
