import json
import matplotlib.pyplot as plt

with open("logs/rl/reward_curve.json", "r") as f:
    rewards = json.load(f)

episodes = range(1, len(rewards) + 1)

plt.figure(figsize=(8,4.5))

plt.plot(
    episodes,
    rewards,
    linewidth=2,
    label="Average Cumulative Reward"
)

plt.xlabel("Training Episode", fontsize=15, fontweight="bold")
plt.ylabel("Average Cumulative Reward", fontsize=15, fontweight="bold")
plt.title("SARA Training Performance", fontsize=18, fontweight="bold", pad=15)
plt.xticks(fontsize=13)
plt.yticks(fontsize=13)
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()

plt.savefig("reward_curve.png", dpi=300)
plt.show()