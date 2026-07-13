import json
import matplotlib.pyplot as plt

# Load reward history
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

plt.xlabel("Training Episode")
plt.ylabel("Average Cumulative Reward")
plt.title("RL Training Performance")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.tight_layout()

plt.savefig("reward_curve.png", dpi=300)
plt.show()