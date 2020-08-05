import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

init = np.array([1.7217, 1.7406, 1.6200, 1.7029, 1.6499, 1.7419, 1.8458, 1.7432, 1.7433, 1.6376])
define = np.array([2.273, 2.2096, 2.1100, 2.1439, 2.0804, 2.5185, 2.1392, 2.0071, 2.0500, 2.3524])
assign = np.array([0.4247, 0.4401, 0.4400, 0.4402, 0.4397, 0.4397, 0.4595, 0.4360, 0.4666, 0.5124])
trigger = np.array([0.8354, 0.8000, 0.4597, 0.8182, 0.4901, 0.5602, 0.4974, 0.8539, 0.8832, 0.8138])
poll = np.array([495.3885, 497.7047, 432.9334, 744.4237, 557.6947, 558.2836, 557.0948, 620.9929, 742.9784, 731.1293])
result = np.array([0.2503, 0.2558, 0.2495, 0.2742, 0.5737, 0.2810, 0.2902, 0.5996, 0.2385, 0.2974])
total = np.array([500.8941, 503.1510, 437.8129, 749.8034, 562.9288, 563.8251, 562.3272, 626.6329, 748.3602, 736.7433])

init_mean = np.mean(init)
define_mean = np.mean(define)
assign_mean = np.mean(assign)
trigger_mean = np.mean(trigger)
poll_mean = np.mean(poll)
result_mean = np.mean(result)
total_mean = np.mean(total)

init_std = np.std(init)
define_std = np.std(define)
assign_std = np.std(assign)
trigger_std = np.std(trigger)
poll_std = np.std(poll)
result_std = np.std(result)
total_std = np.std(total)

values = ['Init', 'Def', 'Assign', 'Trigger', 'Poll', 'Result', 'Total']
x_pos = np.arange(len(values))

means = [init_mean, define_mean, assign_mean, trigger_mean, poll_mean, result_mean, total_mean]
error = [init_std, define_std, assign_std, trigger_std, poll_std, result_std, total_std]

# Build the plot
fig, ax = plt.subplots()
ax.bar(x_pos, means, yerr=error, align='center', alpha=0.8, ecolor='black', capsize=10)

ax.set_yscale("log")
ax.set_ylabel('Time taken in seconds')
ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

ax.set_xticks(x_pos)
ax.set_xticklabels(values)

ax.set_title('Time taken in seconds per evaluation step')
ax.yaxis.grid(True)

# Save the figure and show
plt.tight_layout()
plt.savefig('azure_evaluation_time.png')
plt.show()
