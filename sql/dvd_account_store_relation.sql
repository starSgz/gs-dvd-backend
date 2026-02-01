-- ----------------------------
-- Table structure for dvd_account_store_relation
-- ----------------------------
DROP TABLE IF EXISTS `dvd_account_store_relation`;
CREATE TABLE `dvd_account_store_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `dvd_account_id` bigint NOT NULL COMMENT '账号ID（关联dvd_crawl_account_info.id）',
  `store_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '店铺名称',
  `platform_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '平台ID',
  `product_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '产品ID',
  `is_active` tinyint NOT NULL DEFAULT '1' COMMENT '是否激活（1-激活，0-未激活）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_dvd_account_id` (`dvd_account_id`) USING BTREE,
  KEY `idx_platform_product` (`platform_id`, `product_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='账号-店铺关联表';
