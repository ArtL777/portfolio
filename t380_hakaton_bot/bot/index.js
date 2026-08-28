import { MaxBotApiClient } from '@maxhub/max-bot-api-client';

const BOT_TOKEN = process.env.BOT_TOKEN || 'f9LHodD0cOL8MhpWks45KizUhn6bjVaReKWXsA-2Tk_oeJEitq542C3dael0cRLRf4MwwDWkZTiqk7SbXZGO';
const API_URL = process.env.API_URL || 'https://api.max.ru';
const BRIDGE_API_URL = process.env.BRIDGE_API_URL || 'https://bridge.max.ru';

const bot = new MaxBotApiClient({
  token: BOT_TOKEN,
  apiUrl: API_URL,
});

const userData = new Map();
const sentReminders = new Map();

async function getUserTasks(userId) {
  try {
    const response = await fetch(`${BRIDGE_API_URL}/api/get?key=tasks&userId=${userId}`, {
      headers: {
        'Authorization': `Bearer ${BOT_TOKEN}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data?.value ? JSON.parse(data.value) : [];
    }
  } catch (error) {
    console.error(`Error fetching tasks for user ${userId}:`, error);
  }
  return [];
}

function shouldSendReminder(task, settings) {
  if (!settings.enabled) return false;

  const now = new Date();
  const taskStart = new Date(task.startTime);
  const diffMinutes = (taskStart - now) / (1000 * 60);

  return diffMinutes > 0 && diffMinutes <= settings.beforeTask;
}

async function sendReminder(userId, task) {
  const reminderKey = `${userId}_${task.id}_${new Date(task.startTime).toISOString().split('T')[0]}`;
  
  if (sentReminders.has(reminderKey)) {
    return;
  }

  try {
    const startTime = new Date(task.startTime).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });

    let message = `🔔 Напоминание о деле!\n\n`;
    message += `📌 ${task.name}\n`;
    message += `🕐 Время: ${startTime}\n`;

    if (task.endTime) {
      const endTime = new Date(task.endTime).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
      });
      message += `До: ${endTime}\n`;
    }

    if (task.location) {
      message += `📍 ${task.location}\n`;
    }

    if (task.importance === 'high') {
      message += `\n⚠️ Высокая важность!`;
    }

    await bot.sendMessage({
      userId,
      text: message,
    });

    sentReminders.set(reminderKey, true);
    console.log(`Reminder sent to user ${userId} for task ${task.name}`);
  } catch (error) {
    console.error(`Error sending reminder to user ${userId}:`, error);
  }
}

async function checkMissedTasks(userId, tasks, settings) {
  if (!settings.missedTask) return;

  const now = new Date();
  const today = now.toISOString().split('T')[0];

  for (const task of tasks) {
    const taskDate = new Date(task.startTime).toISOString().split('T')[0];
    const taskTime = new Date(task.startTime);
    const taskEnd = new Date(task.endTime || task.startTime);

    if (taskDate === today && now > taskEnd) {
      try {
        const completed = await getUserCompletedTasks(userId);
        const isCompleted = completed.some(
          c => c.taskId === task.id && c.date === taskDate
        );

        if (!isCompleted) {
          await bot.sendMessage({
            userId,
            text: `⚠️ Вы пропустили дело: ${task.name}\n\nВремя начала: ${taskTime.toLocaleTimeString('ru-RU')}`,
          });
        }
      } catch (error) {
        console.error(`Error checking missed task:`, error);
      }
    }
  }
}

async function getUserCompletedTasks(userId) {
  try {
    const response = await fetch(`${BRIDGE_API_URL}/api/get?key=completedTasks&userId=${userId}`, {
      headers: {
        'Authorization': `Bearer ${BOT_TOKEN}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data?.value ? JSON.parse(data.value) : [];
    }
  } catch (error) {
    console.error(`Error fetching completed tasks:`, error);
  }
  return [];
}

async function checkInactivity(userId, tasks, settings) {
  if (settings.inactiveDays === 0) return;

  try {
    const completed = await getUserCompletedTasks(userId);
    const now = new Date();
    const daysAgo = new Date(now.getTime() - settings.inactiveDays * 24 * 60 * 60 * 1000);
    
    const recentCompletions = completed.filter(c => {
      const completionDate = new Date(c.completedAt);
      return completionDate >= daysAgo;
    });

    if (recentCompletions.length === 0 && tasks.length > 0) {
      await bot.sendMessage({
        userId,
        text: `💔 Ваша крепкая нить ослабевает!\n\nВы давно не выполняли дела. Не забывайте про свои задачи!`,
      });
    }
  } catch (error) {
    console.error(`Error checking inactivity:`, error);
  }
}

async function checkAndSendReminders() {
  try {
    const userIds = Array.from(userData.keys());

    for (const userId of userIds) {
      const userSettings = userData.get(userId);
      const tasks = await getUserTasks(userId);

      for (const task of tasks) {
        if (shouldSendReminder(task, userSettings)) {
          await sendReminder(userId, task);
        }
      }

      await checkMissedTasks(userId, tasks, userSettings);

      const lastInactivityCheck = userSettings.lastInactivityCheck || 0;
      const now = Date.now();
      if (now - lastInactivityCheck > 24 * 60 * 60 * 1000) {
        await checkInactivity(userId, tasks, userSettings);
        userSettings.lastInactivityCheck = now;
      }
    }

    sentReminders.clear();
  } catch (error) {
    console.error('Error in reminder check:', error);
  }
}

bot.onMessage(async (message) => {
  const { userId, text } = message;

  if (!userData.has(userId)) {
    userData.set(userId, {
      enabled: true,
      beforeTask: 15,
      missedTask: true,
      inactiveDays: 3,
      lastInactivityCheck: 0,
    });
  }

  if (text === '/start' || text === '/help') {
    await bot.sendMessage({
      userId,
      text: `Привет! Я бот для управления делами "Крепкая Нить".\n\n` +
            `Я буду напоминать тебе о предстоящих делах и уведомлять о пропущенных задачах.\n\n` +
            `Команды:\n` +
            `/settings - настройки уведомлений\n` +
            `/status - статус уведомлений`,
    });
  } else if (text === '/settings') {
    const settings = userData.get(userId);
    await bot.sendMessage({
      userId,
      text: `Текущие настройки уведомлений:\n\n` +
            `Включены: ${settings.enabled ? 'Да' : 'Нет'}\n` +
            `Напоминать за: ${settings.beforeTask} минут\n` +
            `Уведомлять о пропусках: ${settings.missedTask ? 'Да' : 'Нет'}\n` +
            `Уведомлять о неактивности: ${settings.inactiveDays > 0 ? `Да (через ${settings.inactiveDays} дней)` : 'Нет'}\n\n` +
            `Для изменения настроек используйте мини-приложение.`,
    });
  } else if (text === '/status') {
    const settings = userData.get(userId);
    await bot.sendMessage({
      userId,
      text: `Уведомления ${settings.enabled ? 'включены' : 'выключены'}`,
    });
  } else {
    await bot.sendMessage({
      userId,
      text: `Не понимаю эту команду. Используйте /help для списка команд.`,
    });
  }
});

setInterval(checkAndSendReminders, 60 * 1000);

console.log('Bot started');

export default bot;
