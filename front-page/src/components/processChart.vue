<template>
  <div id="process">
    <div id="chart"></div>

      <el-table :data="getProcessData"
                border
                height="200px">
        <el-table-column 
          fixed="left"
          label="pid"
          prop="id"
          width="150px"
          align="left"
          sortable>
        </el-table-column>
        <el-table-column
          label="内存占用量(%)"
          prop="mem"
          width="150px"
          align="left">
        </el-table-column>
        <el-table-column
          label="CPU占用量(%)"
          prop="cpu"
          width="150px"
          align="left">
        </el-table-column>
        <el-table-column
          label="进程名"
          prop="name"
          width="900px"
          align="left">
        </el-table-column>
        <el-table-column 
          label="操作" 
          fixed="right" 
          width="100px">
          <template slot-scope="scope">
            <template v-if="scope.row.auth">
              <el-button
                type="danger"
                @click="handleKill(scope.row.id)">
                关闭
              </el-button>
            </template>
            <template v-else>
              <el-button
                type="danger"
                disabled>
                关闭
              </el-button>
            </template>
          </template>
        </el-table-column>

      </el-table>

  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import echarts, { ECharts } from 'echarts';
import { Watch, Component } from 'vue-property-decorator';
import { Iprocess } from '@/declare';

@Component
export default class ProcessChart extends Vue {
  public myChart: ECharts | undefined = undefined;

  public option = {
    title: {
      text: '进程监控图',
      x: 'left',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c}%',
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      data: this.getName,
    },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        magicType: {
          show: true,
          type: ['pie', 'funnel'],
        },
        restore: { show: true },
        saveAsImage: { show: true },
      },
    },
    calculable: true,
    series: [
      {
        name: '图例',
        type: 'pie',
        radius: [20, 110],
        center: ['25%', '50%'],
        roseType: 'radius',
        label: {
          normal: {
            show: true,
          },
          emphasis: {
            show: true,
          },
        },
        lableLine: {
          normal: {
            show: true,
          },
          emphasis: {
            show: true,
          },
        },
        data: this.getMemData,
      },
      {
        name: '图例',
        type: 'pie',
        radius: [30, 110],
        center: ['75%', '50%'],
        roseType: 'radius',
        label: {
          normal: {
            show: true,
          },
          emphasis: {
            show: true,
          },
        },
        lableLine: {
          normal: {
            show: true,
          },
          emphasis: {
            show: true,
          },
        },
        data: this.getCpuData,
      },
    ],
  };

  public get wsocket() {
    return this.$store.state.websocket;
  }

  public get getProcessLabel() {
    return this.$store.state.processlabel;
  }

  public get getProcessData() {
    return this.$store.state.processes;
  }

  public get getMemData() {
    const mem: object[] = [];
    this.$store.state.processes.map((item: Iprocess) =>
      mem.push({
        value: item.mem,
        name: item.name,
      }),
    );
    return mem;
  }

  public get getCpuData() {
    const cpu: object[] = [];
    this.$store.state.processes.map((item: Iprocess) =>
      cpu.push({
        value: item.cpu,
        name: item.name,
      }),
    );
    return cpu;
  }

  public get getName() {
    const name: string[] = [];
    this.$store.state.processes.map((item: Iprocess) => name.push(item.name));
    return name;
  }

  public mounted() {
    this.myChart = echarts.init(document.getElementById(
      'chart',
    ) as HTMLDivElement);
    const that = this;
    // 监听窗口大小改变事件，动态地调整图大小
    window.addEventListener('resize', () => {
      if (that.myChart !== undefined) {
        // 初始化
        that.myChart.resize();
      }
    });
  }

  @Watch('getProcessLabel')
  public changeTab() {
    if (this.myChart !== undefined) {
      this.myChart.resize();
      this.myChart.setOption(this.option);
    }
  }

  @Watch('getCpuData')
  public draw() {
    if (this.myChart === undefined) {
      this.myChart = echarts.init(document.getElementById(
        'cpu',
      ) as HTMLDivElement);
      this.myChart.setOption(this.option);
    } else {
      // 有激活数据或者第一次传入数据，跟随父组件大小
      this.myChart.resize();
      // watcher无法监控data改变，所以只能重新赋值
      console.log(this.getMemData);
      console.log(this.getCpuData);
      this.option.series[0].data = this.getMemData;
      this.option.series[1].data = this.getCpuData;
      this.option.legend.data = this.getName;
      this.myChart.setOption(this.option);
    }
  }

  public handleKill(pid: string) {
    this.wsocket.send(
      JSON.stringify({
        id: pid,
        hostid: this.$store.state.active,
      }),
    );
  }
}
</script>

<style scoped>
#process {
  width: 100%;
  height: 95%;
}
#chart {
  width: 100%;
  height: 60%;
}
canvas {
  height: 100%;
  width: 100%;
}
.table {
  width: 100%;
  height: 100%;
}
</style>

