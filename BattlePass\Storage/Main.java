package me.yourname.testplugin;

import org.bukkit.plugin.java.JavaPlugin;

public class Main extends JavaPlugin {
    @Override
    public void onEnable() {
        getLogger().info("Test Plugin enabled!");
        getCommand("test").setExecutor(new TestCommand(this));
    }

    @Override
    public void onDisable() {
        getLogger().info("Test Plugin disabled!");
    }
}
