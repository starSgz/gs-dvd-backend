/*
 Navicat Premium Data Transfer

 Source Server         : 服务器
 Source Server Type    : MySQL
 Source Server Version : 90500
 Source Host           : 172.16.92.11:3306
 Source Schema         : oc

 Target Server Type    : MySQL
 Target Server Version : 90500
 File Encoding         : 65001

 Date: 07/01/2026 17:13:26
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sys_config
-- ----------------------------
DROP TABLE IF EXISTS `sys_config`;
CREATE TABLE `sys_config`  (
  `config_id` int NOT NULL AUTO_INCREMENT COMMENT '参数主键',
  `config_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '参数名称',
  `config_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '参数键名',
  `config_value` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '参数键值',
  `config_type` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'N' COMMENT '系统内置（Y是 N否）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`config_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '参数配置表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_config
-- ----------------------------
INSERT INTO `sys_config` VALUES (1, '主框架页-默认皮肤样式名称', 'sys.index.skinName', 'skin-blue', 'Y', 'admin', '2026-01-07 06:13:34', '', NULL, '蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow');
INSERT INTO `sys_config` VALUES (2, '用户管理-账号初始密码', 'sys.user.initPassword', '123456', 'Y', 'admin', '2026-01-07 06:13:34', '', NULL, '初始化密码 123456');
INSERT INTO `sys_config` VALUES (3, '主框架页-侧边栏主题', 'sys.index.sideTheme', 'theme-dark', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '深色主题theme-dark，浅色主题theme-light');
INSERT INTO `sys_config` VALUES (4, '账号自助-验证码开关', 'sys.account.captchaEnabled', 'true', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '是否开启验证码功能（true开启，false关闭）');
INSERT INTO `sys_config` VALUES (5, '账号自助-是否开启用户注册功能', 'sys.account.registerUser', 'false', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '是否开启注册用户功能（true开启，false关闭）');
INSERT INTO `sys_config` VALUES (6, '用户登录-黑名单列表', 'sys.login.blackIPList', '', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '设置登录IP黑名单限制，多个匹配项以;分隔，支持匹配（*通配、网段）');
INSERT INTO `sys_config` VALUES (7, '用户管理-初始密码修改策略', 'sys.account.initPasswordModify', '1', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '0：初始密码修改策略关闭，没有任何提示，1：提醒用户，如果未修改初始密码，则在登录时就会提醒修改密码对话框');
INSERT INTO `sys_config` VALUES (8, '用户管理-账号密码更新周期', 'sys.account.passwordValidateDays', '0', 'Y', 'admin', '2026-01-07 06:13:35', '', NULL, '密码更新周期（填写数字，数据初始化值为0不限制，若修改必须为大于0小于365的正整数），如果超过这个周期登录系统时，则在登录时就会提醒修改密码对话框');

-- ----------------------------
-- Table structure for sys_dept
-- ----------------------------
DROP TABLE IF EXISTS `sys_dept`;
CREATE TABLE `sys_dept`  (
  `dept_id` bigint NOT NULL AUTO_INCREMENT COMMENT '部门id',
  `parent_id` bigint NULL DEFAULT 0 COMMENT '父部门id',
  `ancestors` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '祖级列表',
  `dept_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '部门名称',
  `order_num` int NULL DEFAULT 0 COMMENT '显示顺序',
  `leader` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '负责人',
  `phone` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '邮箱',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '部门状态（0正常 1停用）',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`dept_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 200 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '部门表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_dept
-- ----------------------------
INSERT INTO `sys_dept` VALUES (100, 0, '0', '集团总公司', 0, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (101, 100, '0,100', '深圳分公司', 1, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (102, 100, '0,100', '长沙分公司', 2, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (103, 101, '0,100,101', '研发部门', 1, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (104, 101, '0,100,101', '市场部门', 2, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (105, 101, '0,100,101', '测试部门', 3, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (106, 101, '0,100,101', '财务部门', 4, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (107, 101, '0,100,101', '运维部门', 5, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (108, 102, '0,100,102', '市场部门', 1, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);
INSERT INTO `sys_dept` VALUES (109, 102, '0,100,102', '财务部门', 2, '年糕', '15888888888', 'niangao@qq.com', '0', '0', 'admin', '2026-01-07 06:13:29', '', NULL);

-- ----------------------------
-- Table structure for sys_dict_data
-- ----------------------------
DROP TABLE IF EXISTS `sys_dict_data`;
CREATE TABLE `sys_dict_data`  (
  `dict_code` bigint NOT NULL AUTO_INCREMENT COMMENT '字典编码',
  `dict_sort` int NULL DEFAULT 0 COMMENT '字典排序',
  `dict_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典标签',
  `dict_value` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典键值',
  `dict_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典类型',
  `css_class` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '样式属性（其他样式扩展）',
  `list_class` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '表格回显样式',
  `is_default` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'N' COMMENT '是否默认（Y是 N否）',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`dict_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '字典数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_dict_data
-- ----------------------------
INSERT INTO `sys_dict_data` VALUES (1, 1, '男', '0', 'sys_user_sex', '', '', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '性别男');
INSERT INTO `sys_dict_data` VALUES (2, 2, '女', '1', 'sys_user_sex', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '性别女');
INSERT INTO `sys_dict_data` VALUES (3, 3, '未知', '2', 'sys_user_sex', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '性别未知');
INSERT INTO `sys_dict_data` VALUES (4, 1, '显示', '0', 'sys_show_hide', '', 'primary', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '显示菜单');
INSERT INTO `sys_dict_data` VALUES (5, 2, '隐藏', '1', 'sys_show_hide', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '隐藏菜单');
INSERT INTO `sys_dict_data` VALUES (6, 1, '正常', '0', 'sys_normal_disable', '', 'primary', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '正常状态');
INSERT INTO `sys_dict_data` VALUES (7, 2, '停用', '1', 'sys_normal_disable', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '停用状态');
INSERT INTO `sys_dict_data` VALUES (8, 1, '正常', '0', 'sys_job_status', '', 'primary', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '正常状态');
INSERT INTO `sys_dict_data` VALUES (9, 2, '暂停', '1', 'sys_job_status', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '停用状态');
INSERT INTO `sys_dict_data` VALUES (10, 1, '默认', 'default', 'sys_job_group', '', '', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '默认分组');
INSERT INTO `sys_dict_data` VALUES (11, 2, '数据库', 'sqlalchemy', 'sys_job_group', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '数据库分组');
INSERT INTO `sys_dict_data` VALUES (12, 3, 'redis', 'redis', 'sys_job_group', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, 'reids分组');
INSERT INTO `sys_dict_data` VALUES (13, 1, '默认', 'default', 'sys_job_executor', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '线程池');
INSERT INTO `sys_dict_data` VALUES (14, 2, '进程池', 'processpool', 'sys_job_executor', '', '', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '进程池');
INSERT INTO `sys_dict_data` VALUES (15, 1, '是', 'Y', 'sys_yes_no', '', 'primary', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '系统默认是');
INSERT INTO `sys_dict_data` VALUES (16, 2, '否', 'N', 'sys_yes_no', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '系统默认否');
INSERT INTO `sys_dict_data` VALUES (17, 1, '通知', '1', 'sys_notice_type', '', 'warning', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '通知');
INSERT INTO `sys_dict_data` VALUES (18, 2, '公告', '2', 'sys_notice_type', '', 'success', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '公告');
INSERT INTO `sys_dict_data` VALUES (19, 1, '正常', '0', 'sys_notice_status', '', 'primary', 'Y', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '正常状态');
INSERT INTO `sys_dict_data` VALUES (20, 2, '关闭', '1', 'sys_notice_status', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '关闭状态');
INSERT INTO `sys_dict_data` VALUES (21, 99, '其他', '0', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '其他操作');
INSERT INTO `sys_dict_data` VALUES (22, 1, '新增', '1', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '新增操作');
INSERT INTO `sys_dict_data` VALUES (23, 2, '修改', '2', 'sys_oper_type', '', 'info', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '修改操作');
INSERT INTO `sys_dict_data` VALUES (24, 3, '删除', '3', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '删除操作');
INSERT INTO `sys_dict_data` VALUES (25, 4, '授权', '4', 'sys_oper_type', '', 'primary', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '授权操作');
INSERT INTO `sys_dict_data` VALUES (26, 5, '导出', '5', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '导出操作');
INSERT INTO `sys_dict_data` VALUES (27, 6, '导入', '6', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '导入操作');
INSERT INTO `sys_dict_data` VALUES (28, 7, '强退', '7', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '强退操作');
INSERT INTO `sys_dict_data` VALUES (29, 8, '生成代码', '8', 'sys_oper_type', '', 'warning', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '生成操作');
INSERT INTO `sys_dict_data` VALUES (30, 9, '清空数据', '9', 'sys_oper_type', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '清空操作');
INSERT INTO `sys_dict_data` VALUES (31, 1, '成功', '0', 'sys_common_status', '', 'primary', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '正常状态');
INSERT INTO `sys_dict_data` VALUES (32, 2, '失败', '1', 'sys_common_status', '', 'danger', 'N', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '停用状态');

-- ----------------------------
-- Table structure for sys_dict_type
-- ----------------------------
DROP TABLE IF EXISTS `sys_dict_type`;
CREATE TABLE `sys_dict_type`  (
  `dict_id` bigint NOT NULL AUTO_INCREMENT COMMENT '字典主键',
  `dict_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典名称',
  `dict_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典类型',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`dict_id`) USING BTREE,
  UNIQUE INDEX `dict_type`(`dict_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '字典类型表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_dict_type
-- ----------------------------
INSERT INTO `sys_dict_type` VALUES (1, '用户性别', 'sys_user_sex', '0', 'admin', '2026-01-07 06:13:33', '', NULL, '用户性别列表');
INSERT INTO `sys_dict_type` VALUES (2, '菜单状态', 'sys_show_hide', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '菜单状态列表');
INSERT INTO `sys_dict_type` VALUES (3, '系统开关', 'sys_normal_disable', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '系统开关列表');
INSERT INTO `sys_dict_type` VALUES (4, '任务状态', 'sys_job_status', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '任务状态列表');
INSERT INTO `sys_dict_type` VALUES (5, '任务分组', 'sys_job_group', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '任务分组列表');
INSERT INTO `sys_dict_type` VALUES (6, '任务执行器', 'sys_job_executor', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '任务执行器列表');
INSERT INTO `sys_dict_type` VALUES (7, '系统是否', 'sys_yes_no', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '系统是否列表');
INSERT INTO `sys_dict_type` VALUES (8, '通知类型', 'sys_notice_type', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '通知类型列表');
INSERT INTO `sys_dict_type` VALUES (9, '通知状态', 'sys_notice_status', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '通知状态列表');
INSERT INTO `sys_dict_type` VALUES (10, '操作类型', 'sys_oper_type', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '操作类型列表');
INSERT INTO `sys_dict_type` VALUES (11, '系统状态', 'sys_common_status', '0', 'admin', '2026-01-07 06:13:34', '', NULL, '登录状态列表');

-- ----------------------------
-- Table structure for sys_logininfor
-- ----------------------------
DROP TABLE IF EXISTS `sys_logininfor`;
CREATE TABLE `sys_logininfor`  (
  `info_id` bigint NOT NULL AUTO_INCREMENT COMMENT '访问ID',
  `user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '用户账号',
  `ipaddr` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '登录IP地址',
  `login_location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '登录地点',
  `browser` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '浏览器类型',
  `os` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '操作系统',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '登录状态（0成功 1失败）',
  `msg` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '提示消息',
  `login_time` datetime NULL DEFAULT NULL COMMENT '访问时间',
  PRIMARY KEY (`info_id`) USING BTREE,
  INDEX `idx_sys_logininfor_s`(`status`) USING BTREE,
  INDEX `idx_sys_logininfor_lt`(`login_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统访问记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_logininfor
-- ----------------------------
INSERT INTO `sys_logininfor` VALUES (100, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '1', '密码错误', '2026-01-07 15:27:06');
INSERT INTO `sys_logininfor` VALUES (101, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '1', '密码错误', '2026-01-07 15:27:12');
INSERT INTO `sys_logininfor` VALUES (102, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '1', '验证码已失效', '2026-01-07 15:30:06');
INSERT INTO `sys_logininfor` VALUES (103, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '1', '验证码错误', '2026-01-07 15:30:06');
INSERT INTO `sys_logininfor` VALUES (104, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '0', '登录成功', '2026-01-07 15:30:09');
INSERT INTO `sys_logininfor` VALUES (105, 'admin', '', '未知', 'Chrome 143', 'Windows 10', '0', '登录成功', '2026-01-07 16:12:07');

-- ----------------------------
-- Table structure for sys_menu
-- ----------------------------
DROP TABLE IF EXISTS `sys_menu`;
CREATE TABLE `sys_menu`  (
  `menu_id` bigint NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
  `menu_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '菜单名称',
  `parent_id` bigint NULL DEFAULT 0 COMMENT '父菜单ID',
  `order_num` int NULL DEFAULT 0 COMMENT '显示顺序',
  `path` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '路由地址',
  `component` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '组件路径',
  `query` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路由参数',
  `route_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '路由名称',
  `is_frame` int NULL DEFAULT 1 COMMENT '是否为外链（0是 1否）',
  `is_cache` int NULL DEFAULT 0 COMMENT '是否缓存（0缓存 1不缓存）',
  `menu_type` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '菜单类型（M目录 C菜单 F按钮）',
  `visible` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '菜单状态（0显示 1隐藏）',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '菜单状态（0正常 1停用）',
  `perms` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '权限标识',
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '#' COMMENT '菜单图标',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '备注',
  PRIMARY KEY (`menu_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2000 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '菜单权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_menu
-- ----------------------------
INSERT INTO `sys_menu` VALUES (1, '系统管理', 0, 1, 'system', NULL, '', '', 1, 0, 'M', '0', '0', '', 'system', 'admin', '2026-01-07 06:13:30', '', NULL, '系统管理目录');
INSERT INTO `sys_menu` VALUES (2, '系统监控', 0, 2, 'monitor', NULL, '', '', 1, 0, 'M', '0', '0', '', 'monitor', 'admin', '2026-01-07 06:13:30', '', NULL, '系统监控目录');
INSERT INTO `sys_menu` VALUES (100, '用户管理', 1, 1, 'user', 'system/user/index', '', '', 1, 0, 'C', '0', '0', 'system:user:list', 'user', 'admin', '2026-01-07 06:13:30', '', NULL, '用户管理菜单');
INSERT INTO `sys_menu` VALUES (101, '角色管理', 1, 2, 'role', 'system/role/index', '', '', 1, 0, 'C', '0', '0', 'system:role:list', 'peoples', 'admin', '2026-01-07 06:13:30', '', NULL, '角色管理菜单');
INSERT INTO `sys_menu` VALUES (102, '菜单管理', 1, 3, 'menu', 'system/menu/index', '', '', 1, 0, 'C', '0', '0', 'system:menu:list', 'tree-table', 'admin', '2026-01-07 06:13:30', '', NULL, '菜单管理菜单');
INSERT INTO `sys_menu` VALUES (103, '部门管理', 1, 4, 'dept', 'system/dept/index', '', '', 1, 0, 'C', '0', '0', 'system:dept:list', 'tree', 'admin', '2026-01-07 06:13:30', '', NULL, '部门管理菜单');
INSERT INTO `sys_menu` VALUES (104, '岗位管理', 1, 5, 'post', 'system/post/index', '', '', 1, 0, 'C', '0', '0', 'system:post:list', 'post', 'admin', '2026-01-07 06:13:30', '', NULL, '岗位管理菜单');
INSERT INTO `sys_menu` VALUES (105, '字典管理', 1, 6, 'dict', 'system/dict/index', '', '', 1, 0, 'C', '0', '0', 'system:dict:list', 'dict', 'admin', '2026-01-07 06:13:30', '', NULL, '字典管理菜单');
INSERT INTO `sys_menu` VALUES (106, '参数设置', 1, 7, 'config', 'system/config/index', '', '', 1, 0, 'C', '0', '0', 'system:config:list', 'edit', 'admin', '2026-01-07 06:13:30', '', NULL, '参数设置菜单');
INSERT INTO `sys_menu` VALUES (107, '通知公告', 1, 8, 'notice', 'system/notice/index', '', '', 1, 0, 'C', '0', '0', 'system:notice:list', 'message', 'admin', '2026-01-07 06:13:30', '', NULL, '通知公告菜单');
INSERT INTO `sys_menu` VALUES (108, '日志管理', 1, 9, 'log', '', '', '', 1, 0, 'M', '0', '0', '', 'log', 'admin', '2026-01-07 06:13:30', '', NULL, '日志管理菜单');
INSERT INTO `sys_menu` VALUES (109, '在线用户', 2, 1, 'online', 'monitor/online/index', '', '', 1, 0, 'C', '0', '0', 'monitor:online:list', 'online', 'admin', '2026-01-07 06:13:30', '', NULL, '在线用户菜单');
INSERT INTO `sys_menu` VALUES (112, '服务监控', 2, 4, 'server', 'monitor/server/index', '', '', 1, 0, 'C', '0', '0', 'monitor:server:list', 'server', 'admin', '2026-01-07 06:13:30', '', NULL, '服务监控菜单');
INSERT INTO `sys_menu` VALUES (113, '缓存监控', 2, 5, 'cache', 'monitor/cache/index', '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list', 'redis', 'admin', '2026-01-07 06:13:30', '', NULL, '缓存监控菜单');
INSERT INTO `sys_menu` VALUES (114, '缓存列表', 2, 6, 'cacheList', 'monitor/cache/list', '', '', 1, 0, 'C', '0', '0', 'monitor:cache:list', 'redis-list', 'admin', '2026-01-07 06:13:30', '', NULL, '缓存列表菜单');
INSERT INTO `sys_menu` VALUES (500, '操作日志', 108, 1, 'operlog', 'monitor/operlog/index', '', '', 1, 0, 'C', '0', '0', 'monitor:operlog:list', 'form', 'admin', '2026-01-07 06:13:30', '', NULL, '操作日志菜单');
INSERT INTO `sys_menu` VALUES (501, '登录日志', 108, 2, 'logininfor', 'monitor/logininfor/index', '', '', 1, 0, 'C', '0', '0', 'monitor:logininfor:list', 'logininfor', 'admin', '2026-01-07 06:13:30', '', NULL, '登录日志菜单');
INSERT INTO `sys_menu` VALUES (1000, '用户查询', 100, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:query', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1001, '用户新增', 100, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:add', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1002, '用户修改', 100, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:edit', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1003, '用户删除', 100, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:remove', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1004, '用户导出', 100, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1005, '用户导入', 100, 6, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:import', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1006, '重置密码', 100, 7, '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:resetPwd', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1007, '角色查询', 101, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:query', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1008, '角色新增', 101, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:add', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1009, '角色修改', 101, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:edit', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1010, '角色删除', 101, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:remove', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1011, '角色导出', 101, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:export', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1012, '菜单查询', 102, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:query', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1013, '菜单新增', 102, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:add', '#', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1014, '菜单修改', 102, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1015, '菜单删除', 102, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1016, '部门查询', 103, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1017, '部门新增', 103, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:add', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1018, '部门修改', 103, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1019, '部门删除', 103, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:dept:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1020, '岗位查询', 104, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1021, '岗位新增', 104, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:add', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1022, '岗位修改', 104, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1023, '岗位删除', 104, 4, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1024, '岗位导出', 104, 5, '', '', '', '', 1, 0, 'F', '0', '0', 'system:post:export', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1025, '字典查询', 105, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1026, '字典新增', 105, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:add', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1027, '字典修改', 105, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1028, '字典删除', 105, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1029, '字典导出', 105, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:dict:export', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1030, '参数查询', 106, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1031, '参数新增', 106, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:add', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1032, '参数修改', 106, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1033, '参数删除', 106, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1034, '参数导出', 106, 5, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:config:export', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1035, '公告查询', 107, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1036, '公告新增', 107, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:add', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1037, '公告修改', 107, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:edit', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1038, '公告删除', 107, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'system:notice:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1039, '操作查询', 500, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1040, '操作删除', 500, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1041, '日志导出', 500, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:operlog:export', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1042, '登录查询', 501, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1043, '登录删除', 501, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:remove', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1044, '日志导出', 501, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:export', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1045, '账户解锁', 501, 4, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:logininfor:unlock', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1046, '在线查询', 109, 1, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:query', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1047, '批量强退', 109, 2, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:batchLogout', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');
INSERT INTO `sys_menu` VALUES (1048, '单条强退', 109, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'monitor:online:forceLogout', '#', 'admin', '2026-01-07 06:13:31', '', NULL, '');

-- ----------------------------
-- Table structure for sys_notice
-- ----------------------------
DROP TABLE IF EXISTS `sys_notice`;
CREATE TABLE `sys_notice`  (
  `notice_id` int NOT NULL AUTO_INCREMENT COMMENT '公告ID',
  `notice_title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '公告标题',
  `notice_type` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '公告类型（1通知 2公告）',
  `notice_content` longblob NULL COMMENT '公告内容',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '公告状态（0正常 1关闭）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`notice_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '通知公告表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_notice
-- ----------------------------
INSERT INTO `sys_notice` VALUES (1, '温馨提醒：2018-07-01 vfadmin新版本发布啦', '2', 0xE696B0E78988E69CACE58685E5AEB9, '0', 'admin', '2026-01-07 06:13:35', '', NULL, '管理员');
INSERT INTO `sys_notice` VALUES (2, '维护通知：2018-07-01 vfadmin系统凌晨维护', '1', 0xE7BBB4E68AA4E58685E5AEB9, '0', 'admin', '2026-01-07 06:13:35', '', NULL, '管理员');

-- ----------------------------
-- Table structure for sys_oper_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_oper_log`;
CREATE TABLE `sys_oper_log`  (
  `oper_id` bigint NOT NULL AUTO_INCREMENT COMMENT '日志主键',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '模块标题',
  `business_type` int NULL DEFAULT 0 COMMENT '业务类型（0其它 1新增 2修改 3删除）',
  `method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '方法名称',
  `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '请求方式',
  `operator_type` int NULL DEFAULT 0 COMMENT '操作类别（0其它 1后台用户 2手机端用户）',
  `oper_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '操作人员',
  `dept_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '部门名称',
  `oper_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '请求URL',
  `oper_ip` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '主机地址',
  `oper_location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '操作地点',
  `oper_param` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '请求参数',
  `json_result` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '返回参数',
  `status` int NULL DEFAULT 0 COMMENT '操作状态（0正常 1异常）',
  `error_msg` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '错误消息',
  `oper_time` datetime NULL DEFAULT NULL COMMENT '操作时间',
  `cost_time` bigint NULL DEFAULT 0 COMMENT '消耗时间',
  PRIMARY KEY (`oper_id`) USING BTREE,
  INDEX `idx_sys_oper_log_bt`(`business_type`) USING BTREE,
  INDEX `idx_sys_oper_log_s`(`status`) USING BTREE,
  INDEX `idx_sys_oper_log_ot`(`oper_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '操作日志记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_oper_log
-- ----------------------------
INSERT INTO `sys_oper_log` VALUES (100, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/116', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"116\"\n  }\n}', '{\"code\": 601, \"msg\": \"存在子菜单,不允许删除\", \"success\": false, \"time\": \"2026-01-07T15:33:15.219096\"}', 1, '存在子菜单,不允许删除', '2026-01-07 15:33:15', 47);
INSERT INTO `sys_oper_log` VALUES (101, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1055', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1055\"\n  }\n}', '{\"code\": 601, \"msg\": \"菜单已分配,不允许删除\", \"success\": false, \"time\": \"2026-01-07T15:33:22.656062\"}', 1, '菜单已分配,不允许删除', '2026-01-07 15:33:23', 61);
INSERT INTO `sys_oper_log` VALUES (102, '角色管理', 2, 'module_admin.controller.role_controller.edit_system_role()', 'PUT', 1, 'admin', '研发部门', '/dev-api/system/role', '', '未知', '{\n  \"json_body\": {\n    \"roleId\": 2,\n    \"roleName\": \"普通角色\",\n    \"roleKey\": \"common\",\n    \"roleSort\": 2,\n    \"dataScope\": \"2\",\n    \"menuCheckStrictly\": true,\n    \"deptCheckStrictly\": true,\n    \"status\": \"0\",\n    \"delFlag\": \"0\",\n    \"createBy\": \"admin\",\n    \"createTime\": \"2026-01-07T06:13:30\",\n    \"updateBy\": \"\",\n    \"updateTime\": null,\n    \"remark\": \"普通角色\",\n    \"admin\": false,\n    \"menuIds\": [\n      1,\n      100,\n      1000,\n      1001,\n      1002,\n      1003,\n      1004,\n      1005,\n      1006,\n      101,\n      1007,\n      1008,\n      1009,\n      1010,\n      1011,\n      102,\n      1012,\n      1013,\n      1014,\n      1015,\n      103,\n      1016,\n      1017,\n      1018,\n      1019,\n      104,\n      1020,\n      1021,\n      1022,\n      1023,\n      1024,\n      105,\n      1025,\n      1026,\n      1027,\n      1028,\n      1029,\n      106,\n      1030,\n      1031,\n      1032,\n      1033,\n      1034,\n      107,\n      1035,\n      1036,\n      1037,\n      1038,\n      108,\n      500,\n      1039,\n      1040,\n      1041,\n      501,\n      1042,\n      1043,\n      1044,\n      1045,\n      2,\n      109,\n      1046,\n      1047,\n      1048,\n      110,\n      1049,\n      1050,\n      1051,\n      1052,\n      1053,\n      1054,\n      111,\n      112,\n      113,\n      114,\n      4\n    ]\n  }\n}', '{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2026-01-07T15:33:59.404371\"}', 0, '', '2026-01-07 15:33:59', 143);
INSERT INTO `sys_oper_log` VALUES (103, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1055', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1055\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:37:46.899419\"}', 0, '', '2026-01-07 15:37:47', 88);
INSERT INTO `sys_oper_log` VALUES (104, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1056', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1056\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:37:50.368130\"}', 0, '', '2026-01-07 15:37:50', 89);
INSERT INTO `sys_oper_log` VALUES (105, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1057', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1057\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:37:53.230699\"}', 0, '', '2026-01-07 15:37:53', 95);
INSERT INTO `sys_oper_log` VALUES (106, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1058', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1058\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:37:58.337642\"}', 0, '', '2026-01-07 15:37:58', 76);
INSERT INTO `sys_oper_log` VALUES (107, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1059', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1059\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:38:01.281439\"}', 0, '', '2026-01-07 15:38:01', 103);
INSERT INTO `sys_oper_log` VALUES (108, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/1060', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1060\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:38:04.031813\"}', 0, '', '2026-01-07 15:38:04', 102);
INSERT INTO `sys_oper_log` VALUES (109, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/116', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"116\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:38:07.285997\"}', 0, '', '2026-01-07 15:38:07', 86);
INSERT INTO `sys_oper_log` VALUES (110, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/4', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"4\"\n  }\n}', '{\"code\": 601, \"msg\": \"菜单已分配,不允许删除\", \"success\": false, \"time\": \"2026-01-07T15:39:47.609048\"}', 1, '菜单已分配,不允许删除', '2026-01-07 15:39:48', 54);
INSERT INTO `sys_oper_log` VALUES (111, '角色管理', 2, 'module_admin.controller.role_controller.edit_system_role()', 'PUT', 1, 'admin', '研发部门', '/dev-api/system/role', '', '未知', '{\n  \"json_body\": {\n    \"roleId\": 2,\n    \"roleName\": \"普通角色\",\n    \"roleKey\": \"common\",\n    \"roleSort\": 2,\n    \"dataScope\": \"2\",\n    \"menuCheckStrictly\": true,\n    \"deptCheckStrictly\": true,\n    \"status\": \"0\",\n    \"delFlag\": \"0\",\n    \"createBy\": \"admin\",\n    \"createTime\": \"2026-01-07T06:13:30\",\n    \"updateBy\": \"admin\",\n    \"updateTime\": \"2026-01-07T15:33:59\",\n    \"remark\": \"普通角色\",\n    \"admin\": false,\n    \"menuIds\": [\n      1,\n      100,\n      1000,\n      1001,\n      1002,\n      1003,\n      1004,\n      1005,\n      1006,\n      101,\n      1007,\n      1008,\n      1009,\n      1010,\n      1011,\n      102,\n      1012,\n      1013,\n      1014,\n      1015,\n      103,\n      1016,\n      1017,\n      1018,\n      1019,\n      104,\n      1020,\n      1021,\n      1022,\n      1023,\n      1024,\n      105,\n      1025,\n      1026,\n      1027,\n      1028,\n      1029,\n      106,\n      1030,\n      1031,\n      1032,\n      1033,\n      1034,\n      107,\n      1035,\n      1036,\n      1037,\n      1038,\n      108,\n      500,\n      1039,\n      1040,\n      1041,\n      501,\n      1042,\n      1043,\n      1044,\n      1045,\n      2,\n      109,\n      1046,\n      1047,\n      1048,\n      110,\n      1049,\n      1050,\n      1051,\n      1052,\n      1053,\n      1054,\n      111,\n      112,\n      113,\n      114\n    ]\n  }\n}', '{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2026-01-07T15:40:04.775916\"}', 0, '', '2026-01-07 15:40:05', 155);
INSERT INTO `sys_oper_log` VALUES (112, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/4', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"4\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:40:10.142102\"}', 0, '', '2026-01-07 15:40:10', 111);
INSERT INTO `sys_oper_log` VALUES (113, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/dev-api/system/menu/115', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"115\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T15:50:29.869546\"}', 0, '', '2026-01-07 15:50:30', 44);
INSERT INTO `sys_oper_log` VALUES (114, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/117', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"117\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:22:55.648640\"}', 0, '', '2026-01-07 16:22:56', 1424);
INSERT INTO `sys_oper_log` VALUES (115, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/3', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"3\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:24:22.130827\"}', 0, '', '2026-01-07 16:24:22', 35);
INSERT INTO `sys_oper_log` VALUES (116, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/3', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"3\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:32:45.109553\"}', 0, '', '2026-01-07 16:32:45', 1925);
INSERT INTO `sys_oper_log` VALUES (117, '角色管理', 2, 'module_admin.controller.role_controller.edit_system_role()', 'PUT', 1, 'admin', '研发部门', '/system/role', '', '未知', '{\n  \"json_body\": {\n    \"roleId\": 2,\n    \"roleName\": \"普通角色\",\n    \"roleKey\": \"common\",\n    \"roleSort\": 2,\n    \"dataScope\": \"2\",\n    \"menuCheckStrictly\": true,\n    \"deptCheckStrictly\": true,\n    \"status\": \"0\",\n    \"delFlag\": \"0\",\n    \"createBy\": \"admin\",\n    \"createTime\": \"2026-01-07T06:13:30\",\n    \"updateBy\": \"admin\",\n    \"updateTime\": \"2026-01-07T15:40:05\",\n    \"remark\": \"普通角色\",\n    \"admin\": false,\n    \"menuIds\": [\n      2,\n      1,\n      100,\n      1000,\n      1001,\n      1002,\n      1003,\n      1004,\n      1005,\n      1006,\n      101,\n      1007,\n      1008,\n      1009,\n      1010,\n      1011,\n      102,\n      1012,\n      1013,\n      1014,\n      1015,\n      103,\n      1016,\n      1017,\n      1018,\n      1019,\n      104,\n      1020,\n      1021,\n      1022,\n      1023,\n      1024,\n      105,\n      1025,\n      1026,\n      1027,\n      1028,\n      1029,\n      106,\n      1030,\n      1031,\n      1032,\n      1033,\n      1034,\n      107,\n      1035,\n      1036,\n      1037,\n      1038,\n      108,\n      500,\n      1039,\n      1040,\n      1041,\n      501,\n      1042,\n      1043,\n      1044,\n      1045,\n      109,\n      1046,\n      1047,\n      1048,\n      112,\n      113,\n      114\n    ]\n  }\n}', '{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2026-01-07T16:34:43.561958\"}', 0, '', '2026-01-07 16:34:44', 50);
INSERT INTO `sys_oper_log` VALUES (118, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/111', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"111\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:35:57.767508\"}', 0, '', '2026-01-07 16:35:58', 31);
INSERT INTO `sys_oper_log` VALUES (119, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1049', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1049\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:37:59.880045\"}', 0, '', '2026-01-07 16:38:00', 54);
INSERT INTO `sys_oper_log` VALUES (120, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1050', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1050\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:02.553167\"}', 0, '', '2026-01-07 16:38:02', 83);
INSERT INTO `sys_oper_log` VALUES (121, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1051', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1051\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:05.415580\"}', 0, '', '2026-01-07 16:38:05', 42);
INSERT INTO `sys_oper_log` VALUES (122, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1052', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1052\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:07.476826\"}', 0, '', '2026-01-07 16:38:07', 26);
INSERT INTO `sys_oper_log` VALUES (123, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1053', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1053\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:10.452731\"}', 0, '', '2026-01-07 16:38:10', 31);
INSERT INTO `sys_oper_log` VALUES (124, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/1054', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"1054\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:13.282247\"}', 0, '', '2026-01-07 16:38:13', 100);
INSERT INTO `sys_oper_log` VALUES (125, '菜单管理', 3, 'module_admin.controller.menu_controller.delete_system_menu()', 'DELETE', 1, 'admin', '研发部门', '/system/menu/110', '', '未知', '{\n  \"path_params\": {\n    \"menu_ids\": \"110\"\n  }\n}', '{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2026-01-07T16:38:16.434955\"}', 0, '', '2026-01-07 16:38:16', 27);

-- ----------------------------
-- Table structure for sys_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_post`;
CREATE TABLE `sys_post`  (
  `post_id` bigint NOT NULL AUTO_INCREMENT COMMENT '岗位ID',
  `post_code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '岗位编码',
  `post_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '岗位名称',
  `post_sort` int NOT NULL COMMENT '显示顺序',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`post_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '岗位信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_post
-- ----------------------------
INSERT INTO `sys_post` VALUES (1, 'ceo', '董事长', 1, '0', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_post` VALUES (2, 'se', '项目经理', 2, '0', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_post` VALUES (3, 'hr', '人力资源', 3, '0', 'admin', '2026-01-07 06:13:30', '', NULL, '');
INSERT INTO `sys_post` VALUES (4, 'user', '普通员工', 4, '0', 'admin', '2026-01-07 06:13:30', '', NULL, '');

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`  (
  `role_id` bigint NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `role_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称',
  `role_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色权限字符串',
  `role_sort` int NOT NULL COMMENT '显示顺序',
  `data_scope` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '1' COMMENT '数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）',
  `menu_check_strictly` tinyint(1) NULL DEFAULT 1 COMMENT '菜单树选择项是否关联显示',
  `dept_check_strictly` tinyint(1) NULL DEFAULT 1 COMMENT '部门树选择项是否关联显示',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色状态（0正常 1停用）',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`role_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role` VALUES (1, '超级管理员', 'admin', 1, '1', 1, 1, '0', '0', 'admin', '2026-01-07 06:13:30', '', NULL, '超级管理员');
INSERT INTO `sys_role` VALUES (2, '普通角色', 'common', 2, '2', 1, 1, '0', '0', 'admin', '2026-01-07 06:13:30', 'admin', '2026-01-07 16:34:44', '普通角色');

-- ----------------------------
-- Table structure for sys_role_dept
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_dept`;
CREATE TABLE `sys_role_dept`  (
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `dept_id` bigint NOT NULL COMMENT '部门ID',
  PRIMARY KEY (`role_id`, `dept_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色和部门关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role_dept
-- ----------------------------
INSERT INTO `sys_role_dept` VALUES (2, 100);
INSERT INTO `sys_role_dept` VALUES (2, 101);
INSERT INTO `sys_role_dept` VALUES (2, 105);

-- ----------------------------
-- Table structure for sys_role_menu
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_menu`;
CREATE TABLE `sys_role_menu`  (
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `menu_id` bigint NOT NULL COMMENT '菜单ID',
  PRIMARY KEY (`role_id`, `menu_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色和菜单关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role_menu
-- ----------------------------
INSERT INTO `sys_role_menu` VALUES (2, 1);
INSERT INTO `sys_role_menu` VALUES (2, 2);
INSERT INTO `sys_role_menu` VALUES (2, 100);
INSERT INTO `sys_role_menu` VALUES (2, 101);
INSERT INTO `sys_role_menu` VALUES (2, 102);
INSERT INTO `sys_role_menu` VALUES (2, 103);
INSERT INTO `sys_role_menu` VALUES (2, 104);
INSERT INTO `sys_role_menu` VALUES (2, 105);
INSERT INTO `sys_role_menu` VALUES (2, 106);
INSERT INTO `sys_role_menu` VALUES (2, 107);
INSERT INTO `sys_role_menu` VALUES (2, 108);
INSERT INTO `sys_role_menu` VALUES (2, 109);
INSERT INTO `sys_role_menu` VALUES (2, 112);
INSERT INTO `sys_role_menu` VALUES (2, 113);
INSERT INTO `sys_role_menu` VALUES (2, 114);
INSERT INTO `sys_role_menu` VALUES (2, 500);
INSERT INTO `sys_role_menu` VALUES (2, 501);
INSERT INTO `sys_role_menu` VALUES (2, 1000);
INSERT INTO `sys_role_menu` VALUES (2, 1001);
INSERT INTO `sys_role_menu` VALUES (2, 1002);
INSERT INTO `sys_role_menu` VALUES (2, 1003);
INSERT INTO `sys_role_menu` VALUES (2, 1004);
INSERT INTO `sys_role_menu` VALUES (2, 1005);
INSERT INTO `sys_role_menu` VALUES (2, 1006);
INSERT INTO `sys_role_menu` VALUES (2, 1007);
INSERT INTO `sys_role_menu` VALUES (2, 1008);
INSERT INTO `sys_role_menu` VALUES (2, 1009);
INSERT INTO `sys_role_menu` VALUES (2, 1010);
INSERT INTO `sys_role_menu` VALUES (2, 1011);
INSERT INTO `sys_role_menu` VALUES (2, 1012);
INSERT INTO `sys_role_menu` VALUES (2, 1013);
INSERT INTO `sys_role_menu` VALUES (2, 1014);
INSERT INTO `sys_role_menu` VALUES (2, 1015);
INSERT INTO `sys_role_menu` VALUES (2, 1016);
INSERT INTO `sys_role_menu` VALUES (2, 1017);
INSERT INTO `sys_role_menu` VALUES (2, 1018);
INSERT INTO `sys_role_menu` VALUES (2, 1019);
INSERT INTO `sys_role_menu` VALUES (2, 1020);
INSERT INTO `sys_role_menu` VALUES (2, 1021);
INSERT INTO `sys_role_menu` VALUES (2, 1022);
INSERT INTO `sys_role_menu` VALUES (2, 1023);
INSERT INTO `sys_role_menu` VALUES (2, 1024);
INSERT INTO `sys_role_menu` VALUES (2, 1025);
INSERT INTO `sys_role_menu` VALUES (2, 1026);
INSERT INTO `sys_role_menu` VALUES (2, 1027);
INSERT INTO `sys_role_menu` VALUES (2, 1028);
INSERT INTO `sys_role_menu` VALUES (2, 1029);
INSERT INTO `sys_role_menu` VALUES (2, 1030);
INSERT INTO `sys_role_menu` VALUES (2, 1031);
INSERT INTO `sys_role_menu` VALUES (2, 1032);
INSERT INTO `sys_role_menu` VALUES (2, 1033);
INSERT INTO `sys_role_menu` VALUES (2, 1034);
INSERT INTO `sys_role_menu` VALUES (2, 1035);
INSERT INTO `sys_role_menu` VALUES (2, 1036);
INSERT INTO `sys_role_menu` VALUES (2, 1037);
INSERT INTO `sys_role_menu` VALUES (2, 1038);
INSERT INTO `sys_role_menu` VALUES (2, 1039);
INSERT INTO `sys_role_menu` VALUES (2, 1040);
INSERT INTO `sys_role_menu` VALUES (2, 1041);
INSERT INTO `sys_role_menu` VALUES (2, 1042);
INSERT INTO `sys_role_menu` VALUES (2, 1043);
INSERT INTO `sys_role_menu` VALUES (2, 1044);
INSERT INTO `sys_role_menu` VALUES (2, 1045);
INSERT INTO `sys_role_menu` VALUES (2, 1046);
INSERT INTO `sys_role_menu` VALUES (2, 1047);
INSERT INTO `sys_role_menu` VALUES (2, 1048);

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`  (
  `user_id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `dept_id` bigint NULL DEFAULT NULL COMMENT '部门ID',
  `user_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户账号',
  `nick_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户昵称',
  `user_type` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '00' COMMENT '用户类型（00系统用户）',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '用户邮箱',
  `phonenumber` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '手机号码',
  `sex` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '用户性别（0男 1女 2未知）',
  `avatar` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '头像地址',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '密码',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `login_ip` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '最后登录IP',
  `login_date` datetime NULL DEFAULT NULL COMMENT '最后登录时间',
  `pwd_update_date` datetime NULL DEFAULT NULL COMMENT '密码最后更新时间',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '创建者',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '更新者',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 100 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user` VALUES (1, 103, 'admin', '超级管理员', '00', 'niangao@163.com', '15888888888', '1', '', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '127.0.0.1', '2026-01-07 16:12:07', '2026-01-07 06:13:29', 'admin', '2026-01-07 06:13:29', '', NULL, '管理员');
INSERT INTO `sys_user` VALUES (2, 105, 'niangao', '年糕', '00', 'niangao@qq.com', '15666666666', '1', '', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '127.0.0.1', '2026-01-07 06:13:29', '2026-01-07 06:13:29', 'admin', '2026-01-07 06:13:29', '', NULL, '测试员');

-- ----------------------------
-- Table structure for sys_user_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_user_post`;
CREATE TABLE `sys_user_post`  (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `post_id` bigint NOT NULL COMMENT '岗位ID',
  PRIMARY KEY (`user_id`, `post_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户与岗位关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user_post
-- ----------------------------
INSERT INTO `sys_user_post` VALUES (1, 1);
INSERT INTO `sys_user_post` VALUES (2, 2);

-- ----------------------------
-- Table structure for sys_user_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_user_role`;
CREATE TABLE `sys_user_role`  (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `role_id` bigint NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户和角色关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user_role
-- ----------------------------
INSERT INTO `sys_user_role` VALUES (1, 1);
INSERT INTO `sys_user_role` VALUES (2, 2);

SET FOREIGN_KEY_CHECKS = 1;
