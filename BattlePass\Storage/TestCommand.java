package me.yourname.testplugin;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

public class TestCommand implements CommandExecutor {
    private final Main plugin;

    public TestCommand(Main plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("Эта команда доступна только игрокам!");
            return true;
        }

        // Открытие веб-интерфейса
        openWebInterface(player);
        return true;
    }

    private void openWebInterface(Player player) {
        // Здесь можно вызвать метод отображения веб-интерфейса
        player.sendMessage("Открывается веб-интерфейс...");
        new WebInterface(plugin).show(player);
    }
}
