using System.Text.Json;
using YouAreNotTheFish.Core.Data;

namespace YouAreNotTheFish.Core.Tests.Data;

public class GameDataLoaderTests
{
    private static readonly string DataDir = Path.Combine(
        AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data");

    /// <summary>Helper: find brain_regions.json by trying a few candidate locations.</summary>
    private static string FindBrainRegionsJson()
    {
        // Try relative to project root first, then absolute fallback
        var candidates = new[]
        {
            Path.Combine(DataDir, "brain_regions.json"),
            Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
                "..", "..", "..", "..", "..", "..", "..", "data", "brain_regions.json")),
        };
        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }
        throw new FileNotFoundException(
            "Cannot find brain_regions.json. Tried:\n" + string.Join("\n", candidates));
    }

    [Fact]
    public void LoadBrainRegions_Loads69Regions()
    {
        var path = FindBrainRegionsJson();
        var data = GameDataLoader.LoadBrainRegions(path);

        Assert.NotNull(data);
        Assert.NotNull(data.Regions);
        Assert.Equal(69, data.Regions.Count);
    }

    [Fact]
    public void LoadBrainRegions_EnumFieldsAreParsedCorrectly()
    {
        var path = FindBrainRegionsJson();
        var data = GameDataLoader.LoadBrainRegions(path);

        // Spot-check a cortical region with full profile
        var a1 = data.Regions["TransverseTemporal"];
        Assert.NotNull(a1);
        Assert.Equal(BrainRegionCategory.Cortical, a1.Category);
        Assert.Equal(Timescale.Fast, a1.FunctionProfile.Timescale);
        Assert.Equal(CstcLoop.None, a1.FunctionProfile.CstcLoop);
        Assert.Equal(CstcRole.None, a1.FunctionProfile.CstcRole);
        Assert.Equal(HierarchyDirection.Feedforward, a1.FunctionProfile.HierarchyDirection);
        Assert.Equal(GameplayDomain.SensoryPerception, a1.FunctionProfile.GameplayDomain);
        Assert.Equal(OscillatoryBand.Gamma, a1.FunctionProfile.OscillatoryBand);
        Assert.Equal(Neurotransmitter.Glutamate, a1.FunctionProfile.NeurotransmitterDominant);

        // Spot-check a subcortical region
        var pag = data.Regions["PeriaqueductalGray"];
        Assert.NotNull(pag);
        Assert.Equal(BrainRegionCategory.Brainstem, pag.Category);
        Assert.Equal(CstcLoop.None, pag.FunctionProfile.CstcLoop);

        // Spot-check mirror entries — Grilling #92 D6：镜像复制主变体完整 function_profile + mirror_of 溯源
        //（偏侧化架构 §9.2 T8：展开剖面 = 主变体逐字段相等）
        var lcRight = data.Regions["LocusCoeruleusRight"];
        Assert.NotNull(lcRight);
        Assert.Equal(BrainRegionCategory.Brainstem, lcRight.Category);
        Assert.Equal("LocusCoeruleus", lcRight.FunctionProfile.MirrorOf);
        Assert.Contains(lcRight.FunctionProfile.MirrorOf, data.Regions.Keys); // AC-13 部分断言
        AssertProfilesEqualExceptMirror(
            data.Regions["LocusCoeruleus"].FunctionProfile, lcRight.FunctionProfile);

        var sncRight = data.Regions["SubstantiaNigraParsCompactaRight"];
        Assert.NotNull(sncRight);
        Assert.Equal("SubstantiaNigraParsCompacta", sncRight.FunctionProfile.MirrorOf);
        AssertProfilesEqualExceptMirror(
            data.Regions["SubstantiaNigraParsCompacta"].FunctionProfile, sncRight.FunctionProfile);
    }

    [Fact]
    public void LoadBrainRegions_AllEnumsParseWithoutNulls_IncludingMirrors()
    {
        var path = FindBrainRegionsJson();
        var data = GameDataLoader.LoadBrainRegions(path);

        foreach (var (fid, region) in data.Regions)
        {
            var fp = region.FunctionProfile;

            if (fp.MirrorOf is { } master)
            {
                // 镜像条目（Grilling #92 D6）：枚举字段非 null——展开剖面 = 主变体逐字段相等（T8），
                // mirror_of 仅作溯源注释字段
                Assert.Contains(master, data.Regions.Keys);
                AssertProfilesEqualExceptMirror(data.Regions[master].FunctionProfile, fp);
            }
            else
            {
                // Non-mirror entries: every enum field must be parsed (not null)
                Assert.True(fp.Timescale.HasValue,
                    $"{fid}: Timescale is null for non-mirror entry");
                Assert.True(fp.NeurotransmitterDominant.HasValue,
                    $"{fid}: NeurotransmitterDominant is null for non-mirror entry");
                Assert.True(fp.OscillatoryBand.HasValue,
                    $"{fid}: OscillatoryBand is null for non-mirror entry");
                Assert.True(fp.CstcLoop.HasValue,
                    $"{fid}: CstcLoop is null for non-mirror entry");
                Assert.True(fp.CstcRole.HasValue,
                    $"{fid}: CstcRole is null for non-mirror entry");
                Assert.True(fp.HierarchyDirection.HasValue,
                    $"{fid}: HierarchyDirection is null for non-mirror entry");
                Assert.True(fp.GameplayDomain.HasValue,
                    $"{fid}: GameplayDomain is null for non-mirror entry");
            }
        }
    }

    /// <summary>断言两个功能剖面逐字段相等（除 mirror_of 溯源字段外）——#92 D6 镜像展开契约（T8）。</summary>
    private static void AssertProfilesEqualExceptMirror(FunctionProfile expected, FunctionProfile actual)
    {
        Assert.Equal(expected.PrimaryFunction, actual.PrimaryFunction);
        Assert.Equal(expected.InputTypes, actual.InputTypes); // xUnit 数组断言 = 序列比较
        Assert.Equal(expected.OutputTypes, actual.OutputTypes);
        Assert.Equal(expected.Timescale, actual.Timescale);
        Assert.Equal(expected.NeurotransmitterDominant, actual.NeurotransmitterDominant);
        Assert.Equal(expected.OscillatoryBand, actual.OscillatoryBand);
        Assert.Equal(expected.CstcLoop, actual.CstcLoop);
        Assert.Equal(expected.CstcRole, actual.CstcRole);
        Assert.Equal(expected.HierarchyDirection, actual.HierarchyDirection);
        Assert.Equal(expected.GameplayDomain, actual.GameplayDomain);
    }

    [Fact]
    public void LoadBrainRegions_CategoryCountsMatchExpected()
    {
        var path = FindBrainRegionsJson();
        var data = GameDataLoader.LoadBrainRegions(path);

        var cortical = data.Regions.Values.Count(r => r.Category == BrainRegionCategory.Cortical);
        var subcortical = data.Regions.Values.Count(r => r.Category == BrainRegionCategory.Subcortical);
        var brainstem = data.Regions.Values.Count(r => r.Category == BrainRegionCategory.Brainstem);

        Assert.Equal(44, cortical);
        Assert.Equal(14, subcortical);
        Assert.Equal(11, brainstem);
    }

    // ─── tripartite_model.json ───────────────────────────────────────

    private static string FindTripartiteModelJson()
    {
        var candidates = new[]
        {
            Path.Combine(DataDir, "connectivity", "tripartite_model.json"),
        };
        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }
        throw new FileNotFoundException(
            "Cannot find tripartite_model.json. Tried:\n" + string.Join("\n", candidates));
    }

    [Fact]
    public void LoadTripartiteModel_CountsMatchExpected()
    {
        var path = FindTripartiteModelJson();
        var model = GameDataLoader.LoadTripartiteModel(path);

        Assert.NotNull(model);
        Assert.Equal(51, model.GraphNodes.Count);
        Assert.Equal(51, model.NodeProfiles.Count);
        Assert.Equal(776, model.Corticocortical.Count);
        Assert.Equal(114, model.Brainstem.Count);
        Assert.Equal(47, model.Cstc.Count);
        Assert.Equal(112, model.PrivilegedPathways.Count);
    }

    [Fact]
    public void LoadTripartiteModel_EnumFieldsAreParsed()
    {
        var path = FindTripartiteModelJson();
        var model = GameDataLoader.LoadTripartiteModel(path);

        // Spot-check a graph node
        var a1 = model.GraphNodes["transversetemporal"];
        Assert.Equal(BrainRegionCategory.Cortical, a1.Category);
        Assert.Contains(Timescale.Fast, a1.Timescales);
        Assert.Contains(GameplayDomain.SensoryPerception, a1.GameplayDomains);

        // Spot-check a CC edge
        var cc = model.Corticocortical.First(e =>
            e.Source == "transversetemporal" && e.Target == "caudalanteriorcingulate");
        Assert.Equal(HierarchyDirection.Feedback, cc.Direction);
        Assert.Equal(EdgeRole.Silent, cc.Role);
        Assert.True(cc.EdrProbability > 0);

        // Spot-check a brainstem projection
        var bs = model.Brainstem.First(e => e.Source == "LocusCoeruleus");
        Assert.Equal(BrainstemSystem.LcNe, bs.System);
        Assert.Equal(Neurotransmitter.Norepinephrine, bs.Neurotransmitter);
        Assert.Equal(BrainstemProjectionType.DiffuseBroadcast, bs.Projection);
        Assert.Equal(EdgeRole.Modulating, bs.Role);

        // Spot-check a CSTC edge
        var cstc = model.Cstc.First(e => e.Source == "precentral");
        Assert.Equal(CstcLoop.Somatic, cstc.Loop);
        Assert.Equal(CstcPathway.GoDirect, cstc.Pathway);
        Assert.Equal(CstcStation.CorticalInput, cstc.StationFrom);
        Assert.Equal(CstcStation.StriatalGate, cstc.StationTo);
        Assert.Equal(EdgeRole.Active, cstc.Role);
        Assert.NotEmpty(cstc.FunctionLabel);
    }

    [Fact]
    public void LoadTripartiteModel_CcEdgeSourcesAndTargetsAreGraphNodes()
    {
        var path = FindTripartiteModelJson();
        var model = GameDataLoader.LoadTripartiteModel(path);

        var dkNames = model.GraphNodes.Keys.ToHashSet();
        foreach (var edge in model.Corticocortical)
        {
            Assert.True(dkNames.Contains(edge.Source),
                $"CC edge source '{edge.Source}' not in graph_nodes");
            Assert.True(dkNames.Contains(edge.Target),
                $"CC edge target '{edge.Target}' not in graph_nodes");
        }
    }

    [Fact]
    public void LoadTripartiteModel_BrainstemSourcesAreFunctionalIds()
    {
        // Load brain regions too for cross-check
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());
        var model = GameDataLoader.LoadTripartiteModel(FindTripartiteModelJson());

        var funcIds = regions.Regions.Keys.ToHashSet();
        foreach (var proj in model.Brainstem)
        {
            Assert.True(funcIds.Contains(proj.Source),
                $"Brainstem source '{proj.Source}' not in brain_regions functional_ids");
        }
    }

    [Fact]
    public void LoadTripartiteModel_CstcEdgeSourcesAndTargetsAreGraphNodes()
    {
        var path = FindTripartiteModelJson();
        var model = GameDataLoader.LoadTripartiteModel(path);

        var dkNames = model.GraphNodes.Keys.ToHashSet();
        foreach (var edge in model.Cstc)
        {
            Assert.True(dkNames.Contains(edge.Source),
                $"CSTC edge source '{edge.Source}' not in graph_nodes");
            Assert.True(dkNames.Contains(edge.Target),
                $"CSTC edge target '{edge.Target}' not in graph_nodes");
        }
    }

    [Fact]
    public void LoadTripartiteModel_PrivilegedPathwayFieldsExist()
    {
        var path = FindTripartiteModelJson();
        var model = GameDataLoader.LoadTripartiteModel(path);

        // Check key fields on all privileged pathways
        var dkNames = model.GraphNodes.Keys.ToHashSet();
        foreach (var pp in model.PrivilegedPathways)
        {
            Assert.NotEmpty(pp.Source);
            Assert.NotEmpty(pp.Target);
            Assert.NotEmpty(pp.PathwayClass);
            Assert.True(pp.EdrProbability >= 0 && pp.EdrProbability <= 1,
                $"edr_probability {pp.EdrProbability} out of [0,1] for {pp.Source}→{pp.Target}");
            // AC-14 部分断言：privileged pathway 端点 membership
            Assert.True(dkNames.Contains(pp.Source),
                $"privileged source '{pp.Source}' not in graph_nodes");
            Assert.True(dkNames.Contains(pp.Target),
                $"privileged target '{pp.Target}' not in graph_nodes");
        }
    }

    // ─── W_sensory.json ─────────────────────────────────────────

    private static string FindWsensoryJson()
    {
        var candidates = new[]
        {
            Path.Combine(DataDir, "connectivity", "W_sensory.json"),
        };
        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }
        throw new FileNotFoundException(
            "Cannot find W_sensory.json. Tried:\n" + string.Join("\n", candidates));
    }

    /// <summary>AC-1: 69×8 int 矩阵 + 8 模态 + RegionIds 69 个且与 Rows.Keys 序一致（#108 Q2 扩列嗅觉/热觉）。</summary>
    [Fact]
    public void LoadWsensory_DimensionsModalitiesAndRegionIds()
    {
        var ws = GameDataLoader.LoadWsensory(FindWsensoryJson());

        Assert.Equal(new[]
        {
            "visual", "auditory", "somatosensory", "pain",
            "social_cognition", "language_cognition", "olfactory", "thermoreception"
        }, ws.Modalities);
        Assert.Equal(69, ws.Matrix.Length);
        Assert.All(ws.Matrix, row => Assert.Equal(8, row.Length));
        Assert.Equal(69, ws.Rows.Count);
        Assert.Equal(69, ws.RegionIds.Length);
        // RegionIds 与 Rows.Keys 序一致（loader 后处理填充）
        Assert.Equal(ws.Rows.Keys, ws.RegionIds);
    }

    /// <summary>AC-2: 69 个 row key ∈ brain_regions functional_ids 且双向双射。</summary>
    [Fact]
    public void LoadWsensory_RowKeysAreFunctionalIdsBidirectional()
    {
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());
        var ws = GameDataLoader.LoadWsensory(FindWsensoryJson());

        var funcIds = regions.Regions.Keys.ToHashSet();
        foreach (var key in ws.Rows.Keys)
        {
            Assert.True(funcIds.Contains(key), $"W_sensory row '{key}' not in functional_ids");
        }
        // 双向：69 个 functional_id 无一行缺失
        foreach (var fid in funcIds)
        {
            Assert.True(ws.Rows.ContainsKey(fid), $"functional_id '{fid}' missing from W_sensory rows");
        }
    }

    /// <summary>AC-8: matrix_2d 行序与 rows 逐行逐模态值一致（69×8 全比对）+ Matrix 行序 == Rows.Keys 序。</summary>
    [Fact]
    public void LoadWsensory_MatrixRowsMatchRowsCellByCell()
    {
        var ws = GameDataLoader.LoadWsensory(FindWsensoryJson());

        var rowKeys = ws.Rows.Keys.ToArray();
        for (int i = 0; i < 69; i++)
        {
            // Matrix 行序 == Rows.Keys 序（sign-off 结转1：显式断言，不依赖 Dictionary 保序）
            Assert.Equal(rowKeys[i], ws.RegionIds[i]);
            for (int j = 0; j < 6; j++)
            {
                var modality = ws.Modalities[j];
                Assert.Equal(ws.Rows[rowKeys[i]][modality], ws.Matrix[i][j]);
            }
        }
    }

    // ─── situation_primitives.json ──────────────────────────────

    private static string FindSituationPrimitivesJson()
    {
        var candidates = new[]
        {
            Path.Combine(DataDir, "connectivity", "situation_primitives.json"),
        };
        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }
        throw new FileNotFoundException(
            "Cannot find situation_primitives.json. Tried:\n" + string.Join("\n", candidates));
    }

    /// <summary>AC-3: LoadSituationPrimitives 返回 27 个 archetype。</summary>
    [Fact]
    public void LoadSituationPrimitives_Loads27Archetypes()
    {
        var sp = GameDataLoader.LoadSituationPrimitives(FindSituationPrimitivesJson());

        Assert.NotNull(sp);
        Assert.Equal(27, sp.Archetypes.Count);
        foreach (var a in sp.Archetypes)
        {
            Assert.NotEmpty(a.Name);
            Assert.NotEmpty(a.DisplayName);
            Assert.NotEmpty(a.Summary);
        }
    }

    /// <summary>AC-4: key_brain_regions 全部 ∈ functional_ids。</summary>
    [Fact]
    public void LoadSituationPrimitives_KeyBrainRegionsAreFunctionalIds()
    {
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());
        var sp = GameDataLoader.LoadSituationPrimitives(FindSituationPrimitivesJson());

        var funcIds = regions.Regions.Keys.ToHashSet();
        foreach (var a in sp.Archetypes)
        {
            foreach (var r in a.KeyBrainRegions)
            {
                Assert.True(funcIds.Contains(r),
                    $"{a.Name} references unknown region '{r}'");
            }
        }
    }

    /// <summary>AC-9: levels_involved 全部 ∈ L0..L5。</summary>
    [Fact]
    public void LoadSituationPrimitives_LevelsAreL0ToL5()
    {
        var sp = GameDataLoader.LoadSituationPrimitives(FindSituationPrimitivesJson());

        var valid = new HashSet<string> { "L0", "L1", "L2", "L3", "L4", "L5" };
        foreach (var a in sp.Archetypes)
        {
            foreach (var level in a.LevelsInvolved)
            {
                Assert.True(valid.Contains(level),
                    $"{a.Name} has invalid level '{level}'");
            }
        }
    }

    /// <summary>
    /// AC-12: primary_networks ∈ 同文件 functional_networks.networks 注册表。
    /// 注册表另读原始 JSON（SituationPrimitives 有意不映射 functional_networks——sign-off 结转4）。
    /// </summary>
    [Fact]
    public void LoadSituationPrimitives_PrimaryNetworksMatchInFileRegistry()
    {
        var path = FindSituationPrimitivesJson();
        var sp = GameDataLoader.LoadSituationPrimitives(path);

        using var doc = JsonDocument.Parse(File.ReadAllText(path));
        var networks = doc.RootElement
            .GetProperty("functional_networks")
            .GetProperty("networks");
        var registry = networks.EnumerateArray()
            .Select(n => n.GetProperty("name").GetString()!)
            .ToHashSet();

        foreach (var a in sp.Archetypes)
        {
            foreach (var n in a.PrimaryNetworks)
            {
                Assert.True(registry.Contains(n),
                    $"{a.Name} network '{n}' not in functional_networks registry");
            }
        }
    }

    // ─── signal_types.json ──────────────────────────────────────

    private static string FindSignalTypesJson()
    {
        var candidates = new[]
        {
            Path.Combine(DataDir, "signal_types.json"),
        };
        foreach (var path in candidates)
        {
            if (File.Exists(path)) return path;
        }
        throw new FileNotFoundException(
            "Cannot find signal_types.json. Tried:\n" + string.Join("\n", candidates));
    }

    /// <summary>AC-5: 4 categories × 18 subtypes（6/5/4/3）+ 异构字段抽查。</summary>
    [Fact]
    public void LoadSignalTypes_CategoriesAndSubtypeCounts()
    {
        var st = GameDataLoader.LoadSignalTypes(FindSignalTypesJson());

        Assert.NotEmpty(st.Description);
        Assert.Equal(4, st.Categories.Count);
        Assert.Equal(6, st.Categories["excitation"].Subtypes.Count);
        Assert.Equal(5, st.Categories["modulation"].Subtypes.Count);
        Assert.Equal(4, st.Categories["gating"].Subtypes.Count);
        Assert.Equal(3, st.Categories["plasticity"].Subtypes.Count);

        // 异构字段抽查（spec §2.2）：excitation 有 oscillatory_band，modulation 有 neurotransmitter，无者 null
        var mc = st.Categories["excitation"].Subtypes["motor_command"];
        Assert.NotNull(mc.OscillatoryBand);
        Assert.Null(mc.Neurotransmitter);
        Assert.Null(mc.Pathway);
        var arousal = st.Categories["modulation"].Subtypes["arousal_NE"];
        Assert.NotNull(arousal.Neurotransmitter);
        Assert.NotNull(arousal.ProjectionPattern);
        Assert.NotNull(arousal.TargetScope);
        Assert.Null(arousal.OscillatoryBand);
        var go = st.Categories["gating"].Subtypes["go_direct"];
        Assert.NotNull(go.Pathway);
        Assert.NotNull(go.Effect);
        var ltp = st.Categories["plasticity"].Subtypes["ltp_consolidation"];
        Assert.NotNull(ltp.Mechanism);
    }

    /// <summary>
    /// AC-10: function_label signal_type 与 input/output_types 全部 ∈ 词表；
    /// signal_type == category/subtype 拼接。
    /// </summary>
    [Fact]
    public void FunctionLabelsAndTypesAreInVocabulary()
    {
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());
        var model = GameDataLoader.LoadTripartiteModel(FindTripartiteModelJson());
        var st = GameDataLoader.LoadSignalTypes(FindSignalTypesJson());

        var vocab = new HashSet<string>();
        foreach (var (cat, catData) in st.Categories)
        {
            foreach (var sub in catData.Subtypes.Keys)
            {
                vocab.Add($"{cat}/{sub}");
            }
        }

        // function_label membership + 内部一致性
        var labels = model.Corticocortical.SelectMany(e => e.FunctionLabel)
            .Concat(model.Brainstem.SelectMany(e => e.FunctionLabel))
            .Concat(model.Cstc.SelectMany(e => e.FunctionLabel))
            .Concat(model.PrivilegedPathways.SelectMany(e => e.FunctionLabel));
        foreach (var l in labels)
        {
            Assert.True(vocab.Contains(l.SignalType),
                $"function_label signal_type '{l.SignalType}' not in vocabulary");
            Assert.Equal($"{l.Category}/{l.Subtype}", l.SignalType);
        }

        // function_profile input/output_types membership
        foreach (var (fid, region) in regions.Regions)
        {
            foreach (var t in region.FunctionProfile.InputTypes)
            {
                Assert.True(vocab.Contains(t), $"{fid} input_type '{t}' not in vocabulary");
            }
            foreach (var t in region.FunctionProfile.OutputTypes)
            {
                Assert.True(vocab.Contains(t), $"{fid} output_type '{t}' not in vocabulary");
            }
        }
    }

    // ─── loader 异常分支（AC-11） ───────────────────────────────

    [Fact]
    public void Loader_MissingFileThrowsFileNotFoundException()
    {
        // 目录存在但文件不存在 → FileNotFoundException（.NET 内建行为）
        var missing = Path.Combine(Path.GetTempPath(), "definitely-not-exists-" + Guid.NewGuid() + ".json");
        Assert.Throws<FileNotFoundException>(
            () => GameDataLoader.LoadWsensory(missing));
    }

    [Fact]
    public void Loader_BadJsonThrowsJsonException()
    {
        var tmp = Path.GetTempFileName();
        File.WriteAllText(tmp, "{ this is not valid json !!!");
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadWsensory(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void Loader_NullLiteralThrowsInvalidOperationException()
    {
        var tmp = Path.GetTempFileName();
        File.WriteAllText(tmp, "null");
        try
        {
            Assert.Throws<InvalidOperationException>(() => GameDataLoader.LoadWsensory(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    // ─── #107：四类边 Role [JsonRequired]（缺 role → JsonException，禁止静默回退 Active(0)）───

    private static string WriteTempJson(string json)
    {
        var tmp = Path.GetTempFileName();
        File.WriteAllText(tmp, json);
        return tmp;
    }

    [Theory]
    [InlineData("{\"brainstem\": [{\"source\": \"LocusCoeruleus\", \"target\": \"x\"}]}")]
    [InlineData("{\"cstc\": [{\"source\": \"x\", \"target\": \"y\"}]}")]
    [InlineData("{\"corticocortical\": [{\"source\": \"x\", \"target\": \"y\"}]}")]
    [InlineData("{\"privileged_pathways\": [{\"source\": \"x\", \"target\": \"y\"}]}")]
    public void Loader_MissingRole_ThrowsJsonException(string badJson)
    {
        var tmp = WriteTempJson(badJson);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadTripartiteModel(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void Loader_NullRole_ThrowsJsonException()
    {
        // "role":null → SnakeCaseEnumConverter.Read GetString() 返回 null → 比较失败抛 JsonException（#106 Q1 实测路径，非 JsonRequired 路径）
        var tmp = WriteTempJson("{\"brainstem\": [{\"source\": \"x\", \"target\": \"y\", \"role\": null}]}");
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadTripartiteModel(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    /// <summary>
    /// 结构完整的**最小** tripartite 文档（P4c 契约新增后必需）。
    ///
    /// 为何需要它：`LoadTripartiteModel` 现在要求在加载期满足 graph_nodes/node_profiles
    /// 数量相等且四种通信原语非空（P4c 结构契约 TP-*）。用 `{"brainstem":[{...}]}` 这种
    /// 只有一个原语的桩，会在**契约校验处**就抛，于是「显式 role 能否正常加载」这条断言
    /// 变成 vacuous——它测的是契约，不是 role。
    ///
    /// ⚠️ 反过来：`Loader_MissingRole_ThrowsJsonException` / `Loader_NullRole_...` 仍可用
    /// 最小桩——它们在反序列化阶段抛（JsonRequired / converter），早于契约校验，语义未变。
    /// </summary>
    private static string MinimalTripartiteJson(string edgeJson) => $$"""
        {
          "graph_nodes": { "x": { "dk_name": "x" } },
          "node_profiles": { "x": {} },
          "corticocortical": [ { "source": "x", "target": "x", "role": "active" } ],
          "cstc": [ { "source": "x", "target": "x", "role": "active" } ],
          "privileged_pathways": [ { "source": "x", "target": "x", "role": "active" } ],
          "brainstem": [ {{edgeJson}} ]
        }
        """;

    [Fact]
    public void Loader_ExplicitRole_LoadsFine()
    {
        // 显式 "role":"active" → 正常通过（验收语义：不能写成「所有最终得到 Active 的情况都失败」）
        var tmp = WriteTempJson(MinimalTripartiteJson("{\"source\": \"x\", \"target\": \"y\", \"role\": \"active\"}"));
        try
        {
            var model = GameDataLoader.LoadTripartiteModel(tmp);
            Assert.Single(model.Brainstem);
            Assert.Equal(EdgeRole.Active, model.Brainstem[0].Role);
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    // ─── AC-13 / AC-14 membership ───────────────────────────────

    /// <summary>AC-13: mirror_of 目标全部 ∈ functional_ids（恰 2 条）。</summary>
    [Fact]
    public void MirrorOfTargetsAreFunctionalIds()
    {
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());

        var funcIds = regions.Regions.Keys.ToHashSet();
        var mirrorCount = 0;
        foreach (var (fid, region) in regions.Regions)
        {
            if (region.FunctionProfile.MirrorOf is string mirror)
            {
                mirrorCount++;
                Assert.True(funcIds.Contains(mirror),
                    $"{fid} mirror_of '{mirror}' not in functional_ids");
            }
        }
        Assert.Equal(2, mirrorCount);
    }

    /// <summary>
    /// AC-14: tripartite 4 类边 1049 条 source/target 全部 ∈ graph_nodes；
    /// brainstem source 同时 ∈ functional_ids（交集语义，spec §五 约束9）。
    /// </summary>
    [Fact]
    public void AllTripartiteEdgesAreWithinGraphNodes()
    {
        var regions = GameDataLoader.LoadBrainRegions(FindBrainRegionsJson());
        var model = GameDataLoader.LoadTripartiteModel(FindTripartiteModelJson());

        var dkNames = model.GraphNodes.Keys.ToHashSet();
        var funcIds = regions.Regions.Keys.ToHashSet();

        void CheckEdges(IEnumerable<(string Source, string Target)> edges,
            string kind, bool sourceMustBeFunctionalId = false)
        {
            foreach (var (s, t) in edges)
            {
                Assert.True(dkNames.Contains(s), $"{kind} source '{s}' not in graph_nodes");
                Assert.True(dkNames.Contains(t), $"{kind} target '{t}' not in graph_nodes");
                if (sourceMustBeFunctionalId)
                {
                    Assert.True(funcIds.Contains(s), $"{kind} source '{s}' not in functional_ids");
                }
            }
        }

        CheckEdges(model.Corticocortical.Select(e => (e.Source, e.Target)), "CC");
        CheckEdges(model.Brainstem.Select(e => (e.Source, e.Target)), "brainstem",
            sourceMustBeFunctionalId: true);
        CheckEdges(model.Cstc.Select(e => (e.Source, e.Target)), "CSTC");
        CheckEdges(model.PrivilegedPathways.Select(e => (e.Source, e.Target)), "privileged");
    }
}
