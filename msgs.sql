
CREATE TABLE `msgs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `User` VARCHAR(255) NOT NULL,
    `Q` TEXT NOT NULL,
    `A` TEXT NOT NULL
);
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (1, '123', '黄瓜是什么老虎', '黄瓜不是动物，它是一种蔬菜，所以二者完全不是一个类别，并没有关联^[4]^');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (2, '123', '局部是什么垃圾', '局部是指可循环使用的物品');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (3, '111', '你是什么垃圾', '很抱歉，我是一个人工智能语言模型，不是一个垃圾');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (4, '222', '苹果是什么垃圾', '苹果属于可回收物');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (5, '222', '黄瓜是什么垃圾', '黄瓜属于湿垃圾/厨余垃圾，是居民日常消费食用的果蔬类食品，最终会变成没有多大利用价值的垃圾，为了环保可以放入厨余垃圾回收桶');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (6, '444', '苹果是什么垃圾', '苹果属于可回收物');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (7, '444', '香蕉是什么东西', '香蕉是一种水果，因为外形长得像弯弯的月亮，所以俗称香蕉');
INSERT INTO `msgs` (`id`, `User`, `Q`, `A`) VALUES (8, '444', '黄椒是什么垃圾', '黄椒属于厨余垃圾，即易腐垃圾');