const Discord = require('discord.js');
const client = new Discord.Client();

client.on('ready', () => {
  console.log('I am ready!');
});

client.on('message', message => {
  if (message.content === 'ping') {
    message.reply('pong');
  }
});

client.login('MjM1MTYzNzQyMDMwMDA0MjI0.Ct2mBA.pmSJ0KTkOiK-9YGdVEvcC3VTsCE');