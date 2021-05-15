class Test():
    def achievementsLoad():
        oldachievements = open("achievements.txt", "r").readlines()

        ##Achievement array layout
        # AchievementName:AchievementDescription:Completed/NotCompleted

        achievementsArray = []
        achievements = []
        for achievement in oldachievements:
            achievement = achievement.strip("\n")
            achievement = achievement.split(":")
            achievementsArray.append(achievement)
        return achievements

Test.achievementsLoad()