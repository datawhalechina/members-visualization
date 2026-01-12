/**
 * GraphQL Schema 定义
 * 使用 GraphQL.js 构建类型系统
 */

import {
  GraphQLSchema,
  GraphQLObjectType,
  GraphQLString,
  GraphQLInt,
  GraphQLFloat,
  GraphQLBoolean,
  GraphQLList,
  GraphQLNonNull,
  GraphQLID,
  GraphQLInputObjectType,
  GraphQLEnumType
} from 'graphql'

import { resolvers } from './resolvers.js'

// 枚举类型：排序方向
const SortOrderEnum = new GraphQLEnumType({
  name: 'SortOrder',
  values: {
    ASC: { value: 'ASC' },
    DESC: { value: 'DESC' }
  }
})

// 枚举类型：成员排序字段
const MemberSortFieldEnum = new GraphQLEnumType({
  name: 'MemberSortField',
  values: {
    FOLLOWERS: { value: 'FOLLOWERS' },
    FOLLOWING: { value: 'FOLLOWING' },
    ORG_REPOS_COUNT: { value: 'ORG_REPOS_COUNT' },
    ORG_TOTAL_STARS: { value: 'ORG_TOTAL_STARS' },
    NAME: { value: 'NAME' }
  }
})

// 输入类型：成员过滤器
const MemberFilterInput = new GraphQLInputObjectType({
  name: 'MemberFilter',
  fields: {
    domain: { type: GraphQLString },
    minFollowers: { type: GraphQLInt },
    maxFollowers: { type: GraphQLInt },
    isOrgMember: { type: GraphQLBoolean }
  }
})

// 对象类型：成员
const MemberType = new GraphQLObjectType({
  name: 'Member',
  fields: {
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: GraphQLString },
    github: { type: GraphQLString },
    avatar: { type: GraphQLString },
    domain: { type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(GraphQLString))) },
    repositories: { type: new GraphQLList(new GraphQLNonNull(GraphQLString)) },
    followers: { type: GraphQLInt },
    following: { type: GraphQLInt },
    org_repos_count: { type: GraphQLInt },
    org_total_stars: { type: GraphQLInt },
    org_total_contributions: { type: GraphQLInt }
  }
})

// 对象类型：研究方向统计
const DomainStatType = new GraphQLObjectType({
  name: 'DomainStat',
  fields: {
    domain: { type: new GraphQLNonNull(GraphQLString) },
    count: { type: new GraphQLNonNull(GraphQLInt) },
    percentage: { type: new GraphQLNonNull(GraphQLFloat) },
    members: { type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(MemberType))) }
  }
})

// 对象类型：统计概览
const StatsOverviewType = new GraphQLObjectType({
  name: 'StatsOverview',
  fields: {
    totalMembers: { type: new GraphQLNonNull(GraphQLInt) },
    totalDomains: { type: new GraphQLNonNull(GraphQLInt) },
    avgDomainsPerMember: { type: new GraphQLNonNull(GraphQLFloat) },
    mostPopularDomain: { type: GraphQLString }
  }
})

// 对象类型：排行榜成员
const RankedMemberType = new GraphQLObjectType({
  name: 'RankedMember',
  fields: {
    rank: { type: new GraphQLNonNull(GraphQLInt) },
    member: { type: new GraphQLNonNull(MemberType) },
    score: { type: new GraphQLNonNull(GraphQLFloat) },
    scoreDisplay: { type: new GraphQLNonNull(GraphQLString) }
  }
})

// 对象类型：排行榜
const LeaderboardType = new GraphQLObjectType({
  name: 'Leaderboard',
  fields: {
    id: { type: new GraphQLNonNull(GraphQLString) },
    title: { type: new GraphQLNonNull(GraphQLString) },
    description: { type: new GraphQLNonNull(GraphQLString) },
    members: { type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(RankedMemberType))) }
  }
})

// 对象类型：Star 历史点
const StarHistoryPointType = new GraphQLObjectType({
  name: 'StarHistoryPoint',
  fields: {
    date: { type: new GraphQLNonNull(GraphQLString) },
    stars: { type: new GraphQLNonNull(GraphQLInt) }
  }
})

// 对象类型：项目信息
const ProjectInfoType = new GraphQLObjectType({
  name: 'ProjectInfo',
  fields: {
    name: { type: new GraphQLNonNull(GraphQLString) },
    stars: { type: new GraphQLNonNull(GraphQLInt) },
    starHistory: { type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(StarHistoryPointType))) }
  }
})

// 对象类型：组织变化信息
const OrganizationChangeType = new GraphQLObjectType({
  name: 'OrganizationChange',
  fields: {
    stars: { type: new GraphQLNonNull(GraphQLInt) },
    repos: { type: new GraphQLNonNull(GraphQLInt) },
    members: { type: new GraphQLNonNull(GraphQLInt) }
  }
})

// 对象类型：组织信息
const OrganizationInfoType = new GraphQLObjectType({
  name: 'OrganizationInfo',
  fields: {
    name: { type: new GraphQLNonNull(GraphQLString) },
    stars: { type: new GraphQLNonNull(GraphQLInt) },
    repos: { type: new GraphQLNonNull(GraphQLInt) },
    members: { type: new GraphQLNonNull(GraphQLInt) },
    change: { type: new GraphQLNonNull(OrganizationChangeType) }
  }
})

// 对象类型：提交统计
const CommitStatsType = new GraphQLObjectType({
  name: 'CommitStats',
  fields: {
    username: { type: new GraphQLNonNull(GraphQLString) },
    totalCommits: { type: new GraphQLNonNull(GraphQLInt) },
    weeklyCommits: { type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(GraphQLInt))) },
    nightCommits: { type: new GraphQLNonNull(GraphQLInt) }
  }
})

// 查询根类型
const QueryType = new GraphQLObjectType({
  name: 'Query',
  fields: {
    // 成员相关查询
    members: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(MemberType))),
      args: {
        filter: { type: MemberFilterInput },
        sortBy: { type: MemberSortFieldEnum },
        sortOrder: { type: SortOrderEnum },
        limit: { type: GraphQLInt },
        offset: { type: GraphQLInt }
      },
      resolve: resolvers.Query.members
    },
    member: {
      type: MemberType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLID) }
      },
      resolve: resolvers.Query.member
    },
    membersByDomain: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(MemberType))),
      args: {
        domain: { type: new GraphQLNonNull(GraphQLString) }
      },
      resolve: resolvers.Query.membersByDomain
    },
    
    // 统计相关查询
    stats: {
      type: new GraphQLNonNull(StatsOverviewType),
      resolve: resolvers.Query.stats
    },
    domainStats: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(DomainStatType))),
      args: {
        limit: { type: GraphQLInt }
      },
      resolve: resolvers.Query.domainStats
    },
    
    // 排行榜相关查询
    leaderboards: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(LeaderboardType))),
      args: {
        filter: { type: MemberFilterInput },
        topCount: { type: GraphQLInt }
      },
      resolve: resolvers.Query.leaderboards
    },
    leaderboard: {
      type: LeaderboardType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLString) },
        filter: { type: MemberFilterInput },
        topCount: { type: GraphQLInt }
      },
      resolve: resolvers.Query.leaderboard
    },
    
    // 项目相关查询
    projects: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(ProjectInfoType))),
      resolve: resolvers.Query.projects
    },
    topProjects: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(ProjectInfoType))),
      args: {
        limit: { type: GraphQLInt }
      },
      resolve: resolvers.Query.topProjects
    },
    
    // 组织相关查询
    organizations: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(OrganizationInfoType))),
      resolve: resolvers.Query.organizations
    },
    
    // 提交统计查询
    commitStats: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(CommitStatsType))),
      args: {
        username: { type: GraphQLString }
      },
      resolve: resolvers.Query.commitStats
    },
    weeklyTopCommitters: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(CommitStatsType))),
      args: {
        limit: { type: GraphQLInt }
      },
      resolve: resolvers.Query.weeklyTopCommitters
    },
    nightOwls: {
      type: new GraphQLNonNull(new GraphQLList(new GraphQLNonNull(CommitStatsType))),
      args: {
        limit: { type: GraphQLInt }
      },
      resolve: resolvers.Query.nightOwls
    }
  }
})

// Mutation 根类型
const MutationType = new GraphQLObjectType({
  name: 'Mutation',
  fields: {
    refreshData: {
      type: new GraphQLNonNull(GraphQLBoolean),
      resolve: resolvers.Mutation.refreshData
    }
  }
})

// 导出 GraphQL Schema
export const schema = new GraphQLSchema({
  query: QueryType,
  mutation: MutationType
})

// 同时导出类型定义字符串（用于文档）
export const typeDefs = `
  # 成员类型
  type Member {
    id: ID!
    name: String
    github: String
    avatar: String
    domain: [String!]!
    repositories: [String!]
    followers: Int
    following: Int
    org_repos_count: Int
    org_total_stars: Int
    org_total_contributions: Int
  }

  # 研究方向统计类型
  type DomainStat {
    domain: String!
    count: Int!
    percentage: Float!
    members: [Member!]!
  }

  # 统计概览类型
  type StatsOverview {
    totalMembers: Int!
    totalDomains: Int!
    avgDomainsPerMember: Float!
    mostPopularDomain: String
  }

  # 排行榜成员类型
  type RankedMember {
    rank: Int!
    member: Member!
    score: Float!
    scoreDisplay: String!
  }

  # 排行榜类型
  type Leaderboard {
    id: String!
    title: String!
    description: String!
    members: [RankedMember!]!
  }

  # 项目信息类型
  type ProjectInfo {
    name: String!
    stars: Int!
    starHistory: [StarHistoryPoint!]!
  }

  # Star 历史点
  type StarHistoryPoint {
    date: String!
    stars: Int!
  }

  # 组织信息类型
  type OrganizationInfo {
    name: String!
    stars: Int!
    repos: Int!
    members: Int!
    change: OrganizationChange!
  }

  # 组织变化信息
  type OrganizationChange {
    stars: Int!
    repos: Int!
    members: Int!
  }

  # 提交统计类型
  type CommitStats {
    username: String!
    totalCommits: Int!
    weeklyCommits: [Int!]!
    nightCommits: Int!
  }

  # 筛选输入类型
  input MemberFilter {
    domain: String
    minFollowers: Int
    maxFollowers: Int
    isOrgMember: Boolean
  }

  # 排序枚举
  enum SortOrder {
    ASC
    DESC
  }

  # 排序字段枚举
  enum MemberSortField {
    FOLLOWERS
    FOLLOWING
    ORG_REPOS_COUNT
    ORG_TOTAL_STARS
    NAME
  }

  # 查询根类型
  type Query {
    members(filter: MemberFilter, sortBy: MemberSortField, sortOrder: SortOrder, limit: Int, offset: Int): [Member!]!
    member(id: ID!): Member
    membersByDomain(domain: String!): [Member!]!
    stats: StatsOverview!
    domainStats(limit: Int): [DomainStat!]!
    leaderboards(filter: MemberFilter, topCount: Int): [Leaderboard!]!
    leaderboard(id: String!, filter: MemberFilter, topCount: Int): Leaderboard
    projects: [ProjectInfo!]!
    topProjects(limit: Int): [ProjectInfo!]!
    organizations: [OrganizationInfo!]!
    commitStats(username: String): [CommitStats!]!
    weeklyTopCommitters(limit: Int): [CommitStats!]!
    nightOwls(limit: Int): [CommitStats!]!
  }

  # 变更根类型
  type Mutation {
    refreshData: Boolean!
  }
`
